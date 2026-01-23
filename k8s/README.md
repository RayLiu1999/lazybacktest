# K3s 部署指南 (Deployment Guide)

本目錄包含將 LazyBacktest 專案部署至 K3s (Kubernetes) 叢集所需的完整設定檔。
這些設定檔採用 **OCI 標準**，完全相容於 K3s 預設的 `containerd` runtime，不依賴 Docker 守護進程。

## 📁 檔案說明

| 檔案名稱 | 用途與詳細說明 |
| :--- | :--- |
| **`config-secret.yaml`** | **配置與機密資訊**<br>包含 `ConfigMap` (一般設定) 與 `Secret` (敏感資訊)。<br>• **ConfigMap**: 定義後端主機、埠號等環境變數。<br>• **Secret**: **最重要的部分**，存放 `DATABASE_URL`。部署前請務必修改此處的資料庫連線字串。 |
| **`backend.yaml`** | **後端服務 (FastAPI)**<br>包含 `Deployment` 與 `Service`。<br>• **Deployment**: 定義後端 Pod 如何運作，包含健康檢查 (Liveness/Readiness Probe) 與環境變數注入。<br>• **Service**: 建立叢集內部的虛擬 IP，讓其他服務能透過 DNS 名稱 (`lazybacktest-backend`) 存取後端。 |
| **`frontend.yaml`** | **前端服務 (React/Nginx)**<br>包含 `Deployment` 與 `Service`。<br>• **Deployment**: 部署前端靜態網頁伺服器。<br>• **Service**: 開放 Port 80 供 Ingress 導流。 |
| **`ingress.yaml`** | **外部入口 (Ingress)**<br>定義外部流量如何進入叢集 (使用 K3s 預設的 Traefik)。<br>• `/api` 開頭的路徑 ➡️ 轉發至 **Backend**<br>• `/` (其他路徑) ➡️ 轉發至 **Frontend** |

---

## 🚀 部署流程

### 步驟 1：準備映像檔 (Images)

由於 K3s 使用 `containerd`，它無法直接讀取您本機 Docker 的映像檔。請選擇以下任一種方式：

#### 🔹 方法 A：使用 Registry (推薦)
將映像檔推送至 Docker Hub 或私有 Registry。
```bash
# 1. Build & Push
docker build -t your-user/lazybacktest-backend:latest ./backend
docker push your-user/lazybacktest-backend:latest

# 2. 修改 yaml
# 請記得更新 backend.yaml 與 frontend.yaml 中的 `image` 欄位
```

#### 🔹 方法 B：手動匯入 (K3s 本地)
如果您直接在 K3s 節點上操作，可將映像檔匯入 containerd。
```bash
# 1. 存成檔案
docker save lazybacktest-backend:latest > backend.tar

# 2. 匯入 K3s
k3s ctr images import backend.tar
```

### 步驟 2：套用設定

請依序執行以下指令進行部署：

1.  **設定環境變數與資料庫連線**
    *請先編輯 `config-secret.yaml`，填入正確的 `DATABASE_URL` (若資料庫在外部，請填寫真實 IP)。*
    ```bash
    kubectl apply -f k8s/config-secret.yaml
    ```

2.  **部署應用程式**
    ```bash
    kubectl apply -f k8s/backend.yaml
    kubectl apply -f k8s/frontend.yaml
    ```

3.  **設定路由與入口**
    ```bash
    kubectl apply -f k8s/ingress.yaml
    ```

### 步驟 3：驗證

執行以下指令確認服務狀態：

```bash
# 查看 Pod 是否皆為 Running
kubectl get pods

# 查看 Ingress IP 位址
kubectl get ingress
```

若 Pod 狀態為 `CrashLoopBackOff`，通常是**資料庫連線失敗**，請檢查 logs：
```bash
kubectl logs deployment/lazybacktest-backend
```
