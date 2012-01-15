import win32service
import win32serviceutil
import win32event
import servicemanager
import winerror
import sys

class PySvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "iskdaemon"
    _svc_display_name_ = "isk-daemon"
    _svc_description_ = "visual search image database"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        # create an event to listen for stop requests on
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
    
    def SvcDoRun(self):
        import servicemanager

        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))

        from iskdaemon import startIskDaemon
        startIskDaemon()
   
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        from twisted.internet import reactor
        reactor.stop()

if __name__ == '__main__':
    import os
    if len(sys.argv) == 1:
        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(PySvc)
            servicemanager.Initialize('iskdaemon', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error, details:
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        win32serviceutil.HandleCommandLine(PySvc)


