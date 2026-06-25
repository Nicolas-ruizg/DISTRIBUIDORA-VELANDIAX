# Despliegue VELANDIAX en servidor Linux

Guia pensada para un servidor Ubuntu con Nginx, Python 3.11+, Node.js 20+ o 22+, Git y dominio configurado.

## 1. Instalar dependencias del sistema

```bash
sudo apt update
sudo apt install -y git nginx python3 python3-venv python3-pip
```

Instalar Node.js con NodeSource:

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
node -v
npm -v
```

## 2. Clonar el repositorio

```bash
cd /var/www
sudo git clone https://github.com/ArleyDev14/VELANDIAX.git
sudo chown -R $USER:$USER /var/www/VELANDIAX
cd /var/www/VELANDIAX
```

## 3. Backend FastAPI

```bash
cd /var/www/VELANDIAX/DISTRIBUIDORA-VELANDIAX
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
nano .env
```

Variables importantes en `.env`:

```env
DB_HOST=...
DB_PORT=5432
DB_SSLMODE=require
DB_NAME=postgres
DB_USER=...
DB_PASSWORD=...

JWT_SECRET=...
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

CORS_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com

SUPABASE_URL=...
SUPABASE_STORAGE_BUCKET=productos
SUPABASE_STORAGE_KEY=...
ENVIO_INTERVALO_SEGUNDOS=30
```

Probar backend:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8001
curl http://127.0.0.1:8001/
```

## 4. Servicio systemd para backend

```bash
sudo nano /etc/systemd/system/velandiax-api.service
```

```ini
[Unit]
Description=VELANDIAX FastAPI Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/VELANDIAX/DISTRIBUIDORA-VELANDIAX
EnvironmentFile=/var/www/VELANDIAX/DISTRIBUIDORA-VELANDIAX/.env
ExecStart=/var/www/VELANDIAX/DISTRIBUIDORA-VELANDIAX/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo chown -R www-data:www-data /var/www/VELANDIAX/DISTRIBUIDORA-VELANDIAX
sudo systemctl daemon-reload
sudo systemctl enable velandiax-api
sudo systemctl start velandiax-api
sudo systemctl status velandiax-api
```

Logs:

```bash
sudo journalctl -u velandiax-api -f
```

## 5. Frontend React/Vite

```bash
cd /var/www/VELANDIAX/velandiax-admin
cp .env.example .env
nano .env
```

Configurar:

```env
VITE_API_URL="https://tu-dominio.com/api"
```

Instalar y compilar:

```bash
npm install
npm run build
```

## 6. Nginx

```bash
sudo nano /etc/nginx/sites-available/velandiax
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    root /var/www/VELANDIAX/velandiax-admin/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/velandiax /etc/nginx/sites-enabled/velandiax
sudo nginx -t
sudo systemctl reload nginx
```

## 7. HTTPS con Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

## 8. Verificaciones

```bash
curl https://tu-dominio.com/api/
curl https://tu-dominio.com/api/productos
sudo systemctl status velandiax-api
sudo systemctl status nginx
```

En navegador:

- `https://tu-dominio.com`
- `https://tu-dominio.com/api/docs`

## 9. Actualizar despliegue despues de cambios

```bash
cd /var/www/VELANDIAX
git pull

cd DISTRIBUIDORA-VELANDIAX
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart velandiax-api

cd ../velandiax-admin
npm install
npm run build
sudo systemctl reload nginx
```
