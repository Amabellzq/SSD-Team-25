from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host='13.58.245.161', debug=True, use_reloader=True)
