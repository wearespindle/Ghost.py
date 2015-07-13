def patch_broken_pipe_error():
    """
    Monkey Patch BaseServer.handle_error to not write a stacktrace to stderr
    on broken pipe. See http://stackoverflow.com/a/7913160
    """
    import sys
    from SocketServer import BaseServer

    handle_error = BaseServer.handle_error

    def my_handle_error(self, request, client_address):
        type, err, tb = sys.exc_info()
        # there might be better ways to detect the specific erro
        if repr(err) == "error(32, 'Broken pipe')":
            # you may ignore it...
            logging.getLogger('mylog').warn(err)
        else:
            handle_error(self, request, client_address)

    BaseServer.handle_error = my_handle_error

patch_broken_pipe_error()
