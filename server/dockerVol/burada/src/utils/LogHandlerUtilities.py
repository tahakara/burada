from werkzeug.serving import WSGIRequestHandler

class RequestLogHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        # Disable the default logging completely
        pass

    def log_request(self, code='-', size='-'):
        forwarded_ip = self.headers.get('Cf-Connecting-IP', self.headers.get('X-Forwarded-For','-'))
        real_ip = self.client_address[0]

        log_message = f'{forwarded_ip} + {real_ip} - - [{self.log_date_time_string()}] "{self.requestline}" {code} {size}'
        print(log_message)
