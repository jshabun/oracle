# Oracle

![Yahoo!](https://img.shields.io/badge/Yahoo!-6001D2?style=for-the-badge&logo=Yahoo!&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

A self-hosted web app that helps you **dominate your Yahoo Fantasy Basketball league**. This project provides real-time draft recommendations, in-season roster move suggestions, and trade analysis — all through a clean, interactive web interface.

## 🚀 Features

### 📊 Draft Mode

* Dynamic player recommendations during your live draft
* Supports **punt strategies** (ignore certain categories)
* Calculates **z-scores** and **Value Over Replacement Player (VORP)**
* Balances team needs across categories and positions

### 🏀 In-Season GM Tools

* Smart roster move suggestions (pickups, drops, substitutions)
* Schedule-based optimizations (back-to-back games, high-volume days)
* Trade analyzer with category impact visualization

### 🌐 Web UI

* Hostable React-based interface
* View recommendations and insights in real time
* Mobile-friendly design for easy draft-day use

## 🛠️ Tech Stack

* **Backend:** FastAPI (Python)
* **Frontend:** React + Tailwind (or DaisyUI)
* **Data:** Yahoo Fantasy Sports API (OAuth integration)
* **Deployment:** Docker & Docker Compose

## 📦 Installation

### 1. Clone the Repository

```bash
 git clone https://github.com/jshabun/oracle.git
 cd oracle
```

### 2. Set Up Yahoo API Credentials

1. Go to [Yahoo Developer Network](https://developer.yahoo.com/fantasysports/guide/)
2. Create an app and generate **Client ID** and **Client Secret**
3. Add them to `.env`:

```bash
YAHOO_CLIENT_ID=your-client-id
YAHOO_CLIENT_SECRET=your-client-secret
LEAGUE_KEY=your-league-key
```

### 3. Run with Docker

```bash
docker-compose up --build
```

Visit `http://localhost:3000` in your browser.

## 📋 Roadmap

* [x] OAuth flow with Yahoo API
* [x] Draft recommendations engine
* [ ] In-season roster optimizer
* [ ] Trade analyzer
* [ ] Advanced category weighting & custom strategies

## 🤝 Contributing

Contributions are welcome! Please open issues or PRs to help improve the project.

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

## 🙌 Acknowledgments

* [Yahoo Fantasy Sports API](https://developer.yahoo.com/fantasysports/guide/)
* Community-driven fantasy basketball strategy resources

---
### ⭐ If this project helps your fantasy season, give it a star on GitHub!
