"""
System Notifications for Jarvis
Windows toast notifications for async task completion.
"""
import sys
import subprocess
import threading


def notify(title: str, message: str, duration: int = 5) -> bool:
    """
    Send a Windows toast notification.
    
    Args:
        title: Notification title
        message: Notification body
        duration: Display duration in seconds
    
    Returns:
        True if notification was sent
    """
    if sys.platform != "win32":
        print(f"[Notification] {title}: {message}")
        return False
    
    try:
        # Try using Windows PowerShell for toast
        ps_script = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

        $template = @"
        <toast duration="short">
            <visual>
                <binding template="ToastGeneric">
                    <text>$($args[0])</text>
                    <text>$($args[1])</text>
                </binding>
            </visual>
            <audio silent="true"/>
        </toast>
"@

        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("JARVIS").Show($toast)
        '''
        
        # Run in background to not block
        def run():
            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        
        threading.Thread(target=run, daemon=True).start()
        return True
        
    except Exception as e:
        # Fallback: simple message box
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)
            return True
        except:
            print(f"[Notification Failed] {title}: {message}")
            return False


def notify_task_complete(task_name: str, summary: str = ""):
    """Notify when an async task completes."""
    msg = summary[:100] if summary else "Ready for your review."
    notify(f"JARVIS: {task_name}", msg)


def notify_error(error: str):
    """Notify on error."""
    notify("JARVIS: Error", error[:100])


def notify_research_complete(topic: str):
    """Notify when research is done."""
    notify("JARVIS: Research Complete", f"Analysis of '{topic}' is ready.")


def notify_deployment_complete(url: str = ""):
    """Notify when deployment is done."""
    msg = f"Live at: {url}" if url else "Deployment successful."
    notify("JARVIS: Deployed", msg)


# Quick test
if __name__ == "__main__":
    notify("JARVIS", "Notification system online. Fascinating.")
