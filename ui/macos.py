"""
macOS 原生窗口操作封装
使用 PyObjC 操作 NSWindow，实现：
  - 透明标题栏（保留系统红绿灯及其全部原生功能）
  - 悬浮胶囊模式（无边框 + 透明 + 置顶 + 缩小）
  - 从悬浮恢复到正常窗口

核心原理：
  - pywebview cocoa 后端在 BrowserView.__init__ 中会对非 frameless 窗口的
    标题栏视图设置 windowBackgroundColor，导致标题栏始终有独立背景。
  - 本模块通过 webview.guilib.BrowserView.instances 直接访问 pywebview 的
    cocoa 原生对象（NSWindow + WKWebView），绕过这个限制。
  - 所有 AppKit 调用通过 callAfter 派发到主线程，线程安全。
  - 非 macOS 平台所有函数均为空操作。
"""

import platform
import traceback

_IS_MACOS = platform.system() == "Darwin"

# 保存正常模式下的窗口状态，用于恢复
_saved_state = {}


# ============================================================
# 公共 API
# ============================================================

def customize_titlebar():
    """
    使系统标题栏透明、隐藏标题文字，内容延伸到标题栏区域。
    保留原生红绿灯按钮及其全部功能（窗口排列、移到其他屏幕等）。
    同时清除 pywebview 内部设置的标题栏视图背景色。
    """
    if not _IS_MACOS:
        return
    try:
        _do_customize_titlebar()
    except Exception as e:
        print(f"[macos] customize_titlebar 失败: {e}")
        traceback.print_exc()


def enter_float_mode():
    """
    进入悬浮胶囊模式：
    - 保存当前窗口 frame / styleMask / level 等
    - 设为无边框 + 全透明（含 WKWebView）+ 置顶
    - 缩小窗口到胶囊尺寸并移动到屏幕顶部居中
    """
    if not _IS_MACOS:
        return False
    try:
        return _do_enter_float_mode()
    except Exception as e:
        print(f"[macos] enter_float_mode 失败: {e}")
        traceback.print_exc()
        return False


def exit_float_mode():
    """
    退出悬浮模式，恢复正常窗口。
    """
    if not _IS_MACOS:
        return False
    try:
        return _do_exit_float_mode()
    except Exception as e:
        print(f"[macos] exit_float_mode 失败: {e}")
        traceback.print_exc()
        return False


def show_window():
    """
    将窗口激活并置于最前方。
    唤醒时调用：确保即使 app 在后台，窗口也能弹出到前面。
    """
    if not _IS_MACOS:
        return
    try:
        import AppKit
        from PyObjCTools import AppHelper

        def _apply():
            _, ns_win, _ = _get_browser_view()
            app = AppKit.NSApplication.sharedApplication()
            # 激活应用（即使不在前台）
            app.activateIgnoringOtherApps_(True)
            if ns_win:
                # 如果窗口被最小化，先恢复
                if ns_win.isMiniaturized():
                    ns_win.deminiaturize_(None)
                ns_win.makeKeyAndOrderFront_(None)

        AppHelper.callAfter(_apply)
    except Exception as e:
        print(f"[macos] show_window 失败: {e}")


def move_window(dx, dy):
    """
    移动窗口位置（相对偏移）。
    由前端拖拽事件驱动，dx/dy 是 CSS 像素偏移量。
    注意：macOS 坐标系 Y 轴向上，所以 dy 要取反。
    """
    if not _IS_MACOS:
        return
    try:
        import AppKit
        from PyObjCTools import AppHelper

        def _apply():
            _, ns_win, _ = _get_browser_view()
            if not ns_win:
                return
            frame = ns_win.frame()
            # macOS 坐标系：Y 向上，网页 Y 向下，所以 dy 取反
            new_origin = AppKit.NSMakePoint(
                frame.origin.x + dx,
                frame.origin.y - dy
            )
            ns_win.setFrameOrigin_(new_origin)

        AppHelper.callAfter(_apply)
    except Exception as e:
        pass  # 拖拽过程中不打印错误，避免刷屏


# ============================================================
# 内部：获取 pywebview cocoa 原生对象
# ============================================================

def _get_browser_view():
    """
    通过 webview.guilib.BrowserView.instances 获取 BrowserView 实例。
    返回 (BrowserView_instance, NSWindow, WKWebView) 或 (None, None, None)。
    """
    try:
        import webview as _wv
        gui = getattr(_wv, 'guilib', None)
        if gui and hasattr(gui, 'BrowserView'):
            instances = gui.BrowserView.instances
            if instances:
                bv = list(instances.values())[0]
                ns_win = getattr(bv, 'window', None)
                wk = getattr(bv, 'webview', None)
                return bv, ns_win, wk
    except Exception as e:
        print(f"[macos] 通过 pywebview 获取原生对象失败: {e}")

    # fallback：从 NSApplication 获取
    try:
        import AppKit
        app = AppKit.NSApplication.sharedApplication()
        ns_win = app.keyWindow()
        if not ns_win:
            for w in (app.windows() or []):
                if w.isVisible():
                    ns_win = w
                    break
        wk = _find_wkwebview(ns_win) if ns_win else None
        return None, ns_win, wk
    except Exception as e:
        print(f"[macos] NSApplication fallback 也失败: {e}")

    return None, None, None


def _find_wkwebview(ns_win):
    """在 NSWindow 的 view hierarchy 中查找 WKWebView"""
    try:
        def _search(view):
            cls_name = view.className()
            if 'WKWebView' in cls_name:
                return view
            for sub in view.subviews():
                r = _search(sub)
                if r:
                    return r
            return None

        cv = ns_win.contentView()
        return _search(cv) if cv else None
    except:
        return None


# ============================================================
# 内部实现
# ============================================================

def _do_customize_titlebar():
    """主线程执行：透明标题栏"""
    import AppKit
    from PyObjCTools import AppHelper

    def _apply():
        _, ns_win, _ = _get_browser_view()
        if not ns_win:
            print("[macos] 未找到 NSWindow，跳过标题栏定制")
            return

        # 1. 标题栏透明 + 隐藏标题文字
        ns_win.setTitlebarAppearsTransparent_(True)
        ns_win.setTitleVisibility_(AppKit.NSWindowTitleHidden)

        # 2. 内容延伸到标题栏区域
        mask = ns_win.styleMask()
        ns_win.setStyleMask_(mask | AppKit.NSWindowStyleMaskFullSizeContentView)

        # 3. 关键：清除 pywebview 在 __init__ 中设置的标题栏视图背景色
        #    pywebview 对非 frameless 窗口执行：
        #    contentView().superview().subviews().lastObject().setBackgroundColor_(windowBgColor)
        #    我们需要把那个视图也设为透明
        try:
            cv = ns_win.contentView()
            if cv:
                superview = cv.superview()
                if superview:
                    subviews = superview.subviews()
                    if subviews and len(subviews) > 0:
                        titlebar_view = subviews.lastObject()
                        titlebar_view.setBackgroundColor_(AppKit.NSColor.clearColor())
                        print("[macos] 标题栏视图背景已清除")
        except Exception as e:
            print(f"[macos] 清除标题栏视图背景失败（不影响功能）: {e}")

        # 4. 窗口背景色
        ns_win.setBackgroundColor_(AppKit.NSColor.windowBackgroundColor())

        # 5. 强制刷新显示
        ns_win.display()
        cv = ns_win.contentView()
        if cv:
            cv.setNeedsLayout_(True)
            cv.setNeedsDisplay_(True)

        print("[macos] 标题栏透明化完成 ✅")

    AppHelper.callAfter(_apply)


def _do_enter_float_mode():
    """主线程执行：进入悬浮模式"""
    import AppKit
    from PyObjCTools import AppHelper

    def _apply():
        global _saved_state
        _, ns_win, wk = _get_browser_view()
        if not ns_win:
            print("[macos] 未找到 NSWindow，无法进入悬浮模式")
            return

        # 保存当前状态
        _saved_state = {
            "frame": ns_win.frame(),
            "styleMask": ns_win.styleMask(),
            "level": ns_win.level(),
            "isOpaque": ns_win.isOpaque(),
            "backgroundColor": ns_win.backgroundColor(),
            "hasShadow": ns_win.hasShadow(),
        }

        # 设为无边框（移除标题栏 + 红绿灯）
        ns_win.setStyleMask_(AppKit.NSWindowStyleMaskBorderless)
        # 置顶
        ns_win.setLevel_(AppKit.NSFloatingWindowLevel)
        # 窗口透明
        ns_win.setOpaque_(False)
        ns_win.setBackgroundColor_(AppKit.NSColor.clearColor())
        ns_win.setHasShadow_(False)
        # 允许通过背景拖动窗口
        ns_win.setMovableByWindowBackground_(True)

        # WKWebView 也需要透明（消除矩形白色底框）
        if wk:
            try:
                wk.setValue_forKey_(False, "drawsBackground")
            except Exception as e:
                print(f"[macos] WKWebView drawsBackground 设置失败: {e}")
                try:
                    wk.setOpaque_(False)
                    wk.setBackgroundColor_(AppKit.NSColor.clearColor())
                except:
                    pass

        # content view 也设透明
        cv = ns_win.contentView()
        if cv:
            try:
                cv.setWantsLayer_(True)
                cv.layer().setBackgroundColor_(AppKit.NSColor.clearColor().CGColor())
            except:
                pass

        # 计算屏幕顶部居中位置
        screen = ns_win.screen() or AppKit.NSScreen.mainScreen()
        sf = screen.visibleFrame()

        capsule_w = 380
        capsule_h = 64
        x = sf.origin.x + (sf.size.width - capsule_w) / 2
        y = sf.origin.y + sf.size.height - capsule_h - 40

        new_frame = AppKit.NSMakeRect(x, y, capsule_w, capsule_h)
        ns_win.setFrame_display_animate_(new_frame, True, True)

        print("[macos] 进入悬浮模式 ✅")

    AppHelper.callAfter(_apply)
    return True


def _do_exit_float_mode():
    """主线程执行：退出悬浮模式"""
    import AppKit
    from PyObjCTools import AppHelper

    def _apply():
        global _saved_state
        _, ns_win, wk = _get_browser_view()
        if not ns_win:
            print("[macos] 未找到 NSWindow，无法退出悬浮模式")
            return

        if not _saved_state:
            print("[macos] 无保存状态，跳过恢复")
            return

        # 恢复 WKWebView 不透明
        if wk:
            try:
                wk.setValue_forKey_(True, "drawsBackground")
            except:
                pass

        # 恢复 styleMask（带回标题栏 + 红绿灯）
        ns_win.setStyleMask_(_saved_state["styleMask"])
        ns_win.setLevel_(_saved_state["level"])
        ns_win.setOpaque_(_saved_state["isOpaque"])
        ns_win.setBackgroundColor_(_saved_state["backgroundColor"])
        ns_win.setHasShadow_(_saved_state["hasShadow"])
        # 恢复原始拖动行为
        ns_win.setMovableByWindowBackground_(False)

        # 恢复窗口尺寸和位置
        ns_win.setFrame_display_animate_(_saved_state["frame"], True, True)

        # 重新应用透明标题栏（含清除标题栏视图背景）
        ns_win.setTitlebarAppearsTransparent_(True)
        ns_win.setTitleVisibility_(AppKit.NSWindowTitleHidden)
        mask = ns_win.styleMask()
        ns_win.setStyleMask_(mask | AppKit.NSWindowStyleMaskFullSizeContentView)
        ns_win.setBackgroundColor_(AppKit.NSColor.windowBackgroundColor())

        # 清除标题栏视图背景
        try:
            cv = ns_win.contentView()
            if cv:
                superview = cv.superview()
                if superview:
                    titlebar_view = superview.subviews().lastObject()
                    titlebar_view.setBackgroundColor_(AppKit.NSColor.clearColor())
        except:
            pass

        ns_win.display()

        _saved_state = {}
        print("[macos] 退出悬浮模式，恢复正常窗口 ✅")

    AppHelper.callAfter(_apply)
    return True
