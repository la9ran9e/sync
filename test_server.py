from sync import Server
import settings


server = Server(settings.SERVER_ADDR)
server.run()
