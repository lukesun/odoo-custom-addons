# odoo-custom-addons

最簡單的安裝方式就是下載zip檔然後解開到odoo addon資料夾
(我是另外開一個odoo-custom-addon,然後在odoo.conf加入設定)

類似這樣
nano /etc/odoo13.conf
##
[options]
; This is the password that allows database operations:
admin_passwd = my_admin_passwd
db_host = False
db_port = False
db_user = odoo13
db_password = False
addons_path = /opt/odoo13/odoo/addons,/opt/odoo13/odoo-custom-addons
##

#設定一個serivce 取名odoo13 
nano /etc/systemd/system/odoo13.service

##
[Unit]
Description=Odoo13
Requires=postgresql.service
After=network.target postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo13
PermissionsStartOnly=true
User=odoo13
Group=odoo13
ExecStart=/opt/odoo13/odoo-venv/bin/python3 /opt/odoo13/odoo/odoo-bin -c /etc/odoo13.conf
StandardOutput=journal+console

[Install]
WantedBy=multi-user.target

##

#再設定開機啟動
systemctl daemon-reload
systemctl enable --now odoo13
systemctl status odoo13

用admin帳號進入odoo後台
先去[設定]打開[開發者模式]

然後再去模組找Access Control模組
直接安裝就可以了

開發時，修改模組檔案後，再去模組
