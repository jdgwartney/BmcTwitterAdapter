import BmcTwitterAdapter


if __name__ == '__main__':
    app = BmcTwitterAdapter.BmcTwitterAdapter()
    try:
        app.manual_run()
    except KeyboardInterrupt:
        print 'Interrupted'
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

