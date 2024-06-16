from webapp import create_app

wsgi = create_app()
wsgi.run(host='0.0.0.0', port=8000)
