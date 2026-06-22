from config.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD
import smtplib
from datetime import datetime, timezone


class NotificationService:
    def __init__(self):
        self.notifications = []

    def send_email(self, to, subject, body):
        if not EMAIL_PASSWORD:
            return False
        try:
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(EMAIL_USER, to, message)
            server.quit()
            return True
        except Exception:
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\nPrioridade: {task.priority}\nStatus: {task.status}"
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': datetime.now(timezone.utc)
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n['user_id'] == user_id]
