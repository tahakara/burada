from flask import Request, g
from sqlalchemy.sql import func, text
from modal import db  # models/__init__.py' db obj 

from utils.UserAgentParserUtilities import parse 

class RequestInfo(db.Model):
    __tablename__ = 'ip_info'
    __table_args__ = {'extend_existing': True}

    id                  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    remote_addr         = db.Column(db.String(45), nullable=False)      # IPv4 (15) + IPv6 (45) güvenli uzunluk
    path                = db.Column(db.Text, nullable=False)            # URL path uzun olabilir
    query_string        = db.Column(db.JSON, nullable=True)             # JSON formatında query string
    referrer            = db.Column(db.Text, nullable=True)             # Tam URL uzun olabileceğinden Text
    x_forwarded_for     = db.Column(db.Text, nullable=True)             # IP zinciri olabileceği için Text
    x_real_ip           = db.Column(db.String(45), nullable=True)       # Tek IP, max 45 karakter
    cf_connecting_ip    = db.Column(db.String(45), nullable=True)
    forwarded           = db.Column(db.Text, nullable=True)             # Format çeşitliliği için Text
    true_client_ip      = db.Column(db.String(45), nullable=True)
    via                 = db.Column(db.String(255), nullable=True)      # Sunucu detayları, string kalabilir
    client_ip           = db.Column(db.String(45), nullable=True)
    x_cluster_client_ip = db.Column(db.String(45), nullable=True)
    x_forwarded         = db.Column(db.Text, nullable=True)             # Zincir olabilir, Text daha güvenli
    x_forwarded_host    = db.Column(db.String(255), nullable=True)
    x_forwarded_proto   = db.Column(db.String(10), nullable=True)       # genelde "http" veya "https"
    host                = db.Column(db.String(255), nullable=False)     # Host adları uzun olabilir
    user_agent          = db.Column(db.Text, nullable=False)            # UA stringleri çok uzun olabilir
    ua_family           = db.Column(db.String(255), nullable=True)      # UA family bilgisi
    ua_version          = db.Column(db.String(255), nullable=True)      # UA version bilgisi
    ua_os               = db.Column(db.String(255), nullable=True)      # OS bilgisi
    ua_os_version       = db.Column(db.String(255), nullable=True)      # OS version bilgisi
    ua_device           = db.Column(db.String(255), nullable=True)      # Device bilgisi
    ua_device_brand     = db.Column(db.String(255), nullable=True)      # Device brand bilgisi
    ua_device_model     = db.Column(db.String(255), nullable=True)      # Device model bilgisi
    ua_is_mobile        = db.Column(db.Boolean, default=False)          # Mobil cihaz mı?
    ua_is_bot           = db.Column(db.Boolean, default=False)          # Bot mu?
    request_uuid        = db.Column(db.String(36), server_default=db.text("UUID()"), nullable=False)     # İsteğe özel bir UUID
    dust_uuid           = db.Column(db.String(36), nullable=True)             # İsteğe özel bir UUID
    dust_device_uuid    = db.Column(db.String(36), nullable=True)             # İsteğe özel bir UUID
    created_at          = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at          = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def _todict(self):
        """Convert the object to a dictionary."""
        return {
            'id':                self.id,
            'remote_addr':       self.remote_addr,
            'path':              self.path,
            'query_string':      self.query_string,
            'referrer':          self.referrer,
            'x_forwarded_for':   self.x_forwarded_for,
            'x_real_ip':         self.x_real_ip,
            'cf_connecting_ip':  self.cf_connecting_ip,
            'forwarded':         self.forwarded,
            'true_client_ip':    self.true_client_ip,
            'via':               self.via,
            'client_ip':         self.client_ip,
            'x_cluster_client_ip':self.x_cluster_client_ip,
            'x_forwarded':       self.x_forwarded,
            'x_forwarded_host':  self.x_forwarded_host,
            'x_forwarded_proto': self.x_forwarded_proto,
            'host':              self.host,
            'user_agent':        self.user_agent,
            'ua_family':         self.ua_family,
            'ua_version':        self.ua_version,
            'ua_os':             self.ua_os,
            'ua_os_version':     self.ua_os_version,
            'ua_device':         self.ua_device,
            'ua_device_brand':   self.ua_device_brand,
            'ua_device_model':   self.ua_device_model,
            'ua_is_mobile':      self.ua_is_mobile,
            'ua_is_bot':         self.ua_is_bot
        }
    
    def _toDictForIP(self):
        """Convert the object to a dictionary for IP information."""
        return {
            # 'remote_addr':       self.remote_addr,
            'remote_addr':       self.cf_connecting_ip,
            # 'path':              self.path,
            # 'query_string':      self.query_string,
            'referrer':          self.referrer,
            'x_forwarded_for':   self.x_forwarded_for,
            'x_real_ip':         self.x_real_ip,
            'cf_connecting_ip':  self.cf_connecting_ip,
            'forwarded':         self.forwarded,
            'true_client_ip':    self.true_client_ip,
            'via':               self.via,
            'client_ip':         self.client_ip,
            'x_cluster_client_ip':self.x_cluster_client_ip,
            'x_forwarded':       self.x_forwarded,
            'x_forwarded_host':  self.x_forwarded_host,
            'x_forwarded_proto': self.x_forwarded_proto,
            # 'host':              self.host
        }

    @staticmethod
    def create_request_info(request: Request, dust: str, dust_device: str) -> 'RequestInfo':
        """Create a new RequestInfo object with the request data."""
        user_agent = request.headers.get('User-Agent')
        parsed_ua = parse(user_agent)

        return RequestInfo(
            remote_addr             =request.remote_addr,
            path                    =request.path,
            query_string            =request.args.to_dict(),
            referrer                =request.referrer,
            x_forwarded_for         =request.headers.get("X-Forwarded-For"),
            x_real_ip               =request.headers.get("X-Real-IP"),
            cf_connecting_ip        =request.headers.get("CF-Connecting-IP"),
            forwarded               =request.headers.get("Forwarded"),
            true_client_ip          =request.headers.get("True-Client-IP"),
            via                     =request.headers.get("Via"),
            client_ip               =request.headers.get("Client-IP"),
            x_cluster_client_ip     =request.headers.get("X-Cluster-Client-IP"),
            x_forwarded             =request.headers.get("X-Forwarded"),
            x_forwarded_host        =request.headers.get("X-Forwarded-Host"),
            x_forwarded_proto       =request.headers.get("X-Forwarded-Proto"),
            host                    =request.headers.get("Host"),
            user_agent              =user_agent,
            ua_family               =parsed_ua.user_agent.family if parsed_ua.user_agent else None,
            ua_version              =('.'.join(str(part) for part in [parsed_ua.user_agent.major, parsed_ua.user_agent.minor, parsed_ua.user_agent.patch, parsed_ua.user_agent.patch_minor] if part is not None) if parsed_ua.user_agent else None),
            ua_os                   =parsed_ua.os.family if parsed_ua.os else None,
            ua_os_version           =('.'.join(str(part) for part in [ parsed_ua.os.major, parsed_ua.os.minor, parsed_ua.os.patch, parsed_ua.os.patch_minor ] if part is not None) if parsed_ua.os else None ),
            ua_device               =parsed_ua.device.family if parsed_ua.device else None,
            ua_device_brand         =parsed_ua.device.brand if parsed_ua.device else None,
            ua_device_model         =parsed_ua.device.model if parsed_ua.device else None,
            ua_is_mobile            =parsed_ua.is_mobile ,
            ua_is_bot               =parsed_ua.is_bot,
            dust_uuid               =dust,
            dust_device_uuid        =dust_device 
        )

