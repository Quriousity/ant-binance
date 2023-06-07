# Procedure
1. Start EC2 instance (AWS)
2. Link Elastic IP to EC2 (AWS)
---
3. Sign up (Binance)
4. Open future account (Binance)
5. Create API (Binance)
6. Preference -> Position Mode -> Hedge Mode (Binance)
7. Adjust leverage (Binance)
---
8. Sign up (Discord)
9. Create server (Discord)
10. Create Webhook (Discord)
---
11. Set configurations (AWS)
12. Create virtual environment (AWS)
13. Install packages (AWS)
14. Run (AWS)

# AWS
1. Start EC2 instance
2. Link Elastic IP to EC2
    ### Make configuration directory
    ```
    mkdir data
    ```
    ### ./data/conf.json
    ```
    vim conf.json
    ```
    ```
    {
        "key": ,
        "secret": ,
        "symbol": "BTCUSDT",
    }
    ```
    ### ./data/discordWebhook.json
    ```
    vim discordWebhook.json
    ```
    ```
    {
        "URL": 
    }
    ```
3. Set configurations (AWS)
4. Create virtual environment (AWS)
5. Install packages (AWS)
6. Run (AWS)

# Binace
1. Sign up
2. Open future account
3. Create API
4. Preference -> Position Mode -> Hedge Mode
5. Adjust leverage
# Discord
1. Sign up
2. Create server
3. Create Webhook
# Virtual Environments
```
python -m venv ant
```
```
source ant/bin/activate
```
### How to deactivates
```
deactivate
```
# Install packages
```
pip install -r requirements.txt
```
# Run
```
nohup python ant.py &
```