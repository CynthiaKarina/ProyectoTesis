from app import create_app

app = create_app()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', '10000'))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true','1','yes']
    app.run(debug=debug, host='0.0.0.0', port=port)