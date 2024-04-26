mkdir -p ~/.streamlit/

cat <<EOF > ~/.streamlit/credentials.toml
[general]
email="hushkao@gmail.com"
EOF

cat <<EOF > ~/.streamlit/secrets.toml
password=$PASSWORD
EOF

cat <<EOF > ~/.streamlit/config.toml
[server]
headless=true
enableCORS=false
port=$PORT

[theme]
primaryColor="#F63366"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif"
EOF
