import time
from daemon import runner

import BmcTwitterAdapter

app = BmcTwitterAdapter.BmcTwitterAdapter()

daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

