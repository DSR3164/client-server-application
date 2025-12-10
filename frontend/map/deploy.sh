sudo rm -r /etc/nginx/sites-available/dist
npm run build
sudo mv dist /etc/nginx/sites-available/dist