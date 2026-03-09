"""
macOS 原生窗口操作封装
使用 PyObjC 操作 NSWindow，实现：
  - 透明标题栏（保留系统红绿灯及其全部原生功能）
  - 悬浮胶囊模式（无边框 + 透明 + 置顶 + 缩小）
  - 从悬浮恢复到正常窗口
所有 AppKit 调用通过 callAfter 派发到主线程，线程安全。
非 macOS 平台所有函数均为空操作。
"""

import platform
import traceback

_IS_MACOS = platform.system() == "Darwin"

# 保存正常模式下的窗口状态，用于恢复
_saved_state = {}

# ============================================================
# 公共 API
# ============================================================

def customize_titlebar(pywebview_window=None):
    """
    使系统标题栏透明、隐藏标题文字，内容延伸到标题栏区域。
    保留原生红绿灯按钮及其全部功能（窗口排列、移到其他屏幕等）。
    """
    if not _IS_MACOS:
        return
    try:
        _do_customize_titlebar(pywebview_window)
    except Exception as e:
        print(f"[macos] customize_titlebar 失败: {e}")
        traceback.print_exc()


def enter_float_mode(pywebview_window=None):
    """
    进入悬浮胶囊模式：
    - 保存当前窗口 frame / styleMask / level 等
    - 设为无边框 + 透明背景 + 置顶
    - 缩小窗口到 380×64 并移动到屏幕顶部居中
    """
    if not _IS_MACOS:
        return False
    try:
        return _do_enter_float_mode(pywebview_window)
    except Exception as e:
        print(f"[macos] enter_float_mode 失败: {e}")
        traceback.print_exc()
        return False


def exit_float_mode(pywebview_window=None):
    """
    退出悬浮模式，恢复正常窗口：
    - 还原 styleMask / level / opaque
    - 恢复原始窗口 frame
    - 重新应用透明标题栏
    """
    if not _IS_MACOS:
        return False
    try:
        return _do_exit_float_mode(pywebview_window)
    except Exception as e:
        print(f"[macos] exit_float_mode 失败: {e}")
        traceback.print_exc()
        return False


# ============================================================
# 内部实现（仅 macOS）
# ============================================================

def _get_nswindow(pywebview_window=None):
    """获取 cocoa NSWindow 对象"""
    try:
        import AppKit
        if pywebview_window and hasattr(pywebview_window, 'gui'):
            # pywebview cocoa 后端
            if hasattr(pywebview_window.gui, 'BrowserView'):
                instances = pywebview_window.gui.BrowserView.instances
                if instances:
                    browser_key = list(instances.keys())[0]
                    browser_view = instances[browser_key]
                    if hasattr(browser_view, 'window'):
                        return browser_view.window
        
        # fallback: 从 NSApplication 获取 keyWindow
        app = AppKit.NSApplication.sharedApplication()
        return app.keyWindow() or (app.windows()[0] if app.windows() else None)
    except Exception as e:
        print(f"[macos] 获取 NSWindow 失败: {e}")
        return None


def _do_customize_titlebar(pywebview_window=None):
    """主线程执行：透明标题栏"""
    import AppKit
    from PyObjCTools import AppHelper

    def _apply():
        ns_win = _get_nswindow(pywebview_window)
        if not ns_win:
            print("[macos] 未找到 NSWindow，跳过标题栏定制")
            return
        
        # 标题栏透明
        ns_win.setTitlebarAppearsTransparent_(True)
        # 隐藏标题文字
        ns_win.setTitleVisibility_(AppKit.NSWindowTitleHidden)
        # 内容延伸到标题栏
        current_mask = ns_win.styleMask()
        ns_win.setStyleMask_(current_mask | AppKit.NSWindowStyleMaskFullSizeContentView)
        # 设置背景色为窗口底色（让 CSS --app-bg 穿透）
        ns_win.setBackgroundColor_(AppKit.NSColor.windowBackgroundColor())
        
        print("[macos] 标题栏透明化完成 ✅")

    AppHelper.callAfter(_apply)


def _do_enter_float_mode(pywebview_window=None):
    """主线程执行：进入悬浮模式"""
    import AppKit
    from PyObjCTools import AppHelper

    def _apply():
        global _saved_state
        ns_win = _get_nswindow(pywebview_window)
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
        
        # 设为无边框（移除标题栏+红绿灯）
        ns_win.setStyleMask_(AppKit.NSWindowStyleMaskBorderless)
        # 置顶
        ns_win.setLevel_(AppKit.NSFloatingWindowLevel)
        # 透明背景
        ns_win.setOpaque_(False)
        ns_win.setBackgroundColor_(AppKit.NSColor.clearColor())
        ns_win.setHasShadow_(False)
        
        # 计算屏幕顶部居中位置
        screen = ns_win.screen() or AppKit.NSScreen.mainScreen()
        screen_frame = screen.visibleFrame()
        
        capsule_w = 380
        capsule_h = 64
        x = screen_frame.origin.x + (screen_frame.size.width - capsule_w) / 2
        y = screen_frame.origin.y + screen_frame.size.height - capsule_h - 40  # 距顶部 40px
        
        new_frame = AppKit.NSMakeRect(x, y, capsule_w, capsule_h)
        ns_win.setFrame_display_animate_(new_frame, True, True)
        
        print("[macos] 进入悬浮模式 ✅")

    AppHelper.callAfter(_apply)
    return True


def _do_exit_float_mode(pywebview_window=None):
    """主线程执行：退出悬浮模式"""
    import AppKit
    from PyObjCTools import AppHelper

    def _apply():
        global _saved_state
        ns_win = _get_nswindow(pywebview_window)
        if not ns_win:
            print("[macos] 未找到 NSWindow，无法退出悬浮模式")
            return
        
        if not _saved_state:
            print("[macos] 无保存状态，跳过恢复")
            return
        
        # 恢复 styleMask（带回标题栏+红绿灯）
        ns_win.setStyleMask_(_saved_state["styleMask"])
        # 恢复层级
        ns_win.setLevel_(_saved_state["level"])
        # 恢复不透明度
        ns_win.setOpaque_(_saved_state["isOpaque"])
        ns_win.setBackgroundColor_(_saved_state["backgroundColor"])
        ns_win.setHasShadow_(_saved_state["hasShadow"])
        
        # 恢复窗口尺寸和位置
        ns_win.setFrame_display_animate_(_saved_state["frame"], True, True)
        
        # 重新应用透明标题栏
        ns_win.setTitlebarAppearsTransparent_(True)
        ns_win.setTitleVisibility_(AppKit.NSWindowTitleHidden)
        current_mask = ns_win.styleMask()
        ns_win.setStyleMask_(current_mask | AppKit.NSWindowStyleMaskFullSizeContentView)
        ns_win.setBackgroundColor_(AppKit.NSColor.windowBackgroundColor())
        
        _saved_state = {}
        print("[macos] 退出悬浮模式，恢复正常窗口 ✅")

    AppHelper.callAfter(_apply)
    return True
