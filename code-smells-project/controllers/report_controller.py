import models.report_model as report_model


class ReportController:

    def sales_report(self):
        report = report_model.get_sales_report()
        return {"dados": report, "sucesso": True}, 200

    def health_check(self):
        return {"status": "ok", "database": "connected"}, 200
