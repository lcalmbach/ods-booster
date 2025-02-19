txt = {
    "info": """# ODS Booster
### **Fast ODS Data Caching Application**

#### **Overview**
ODS (OpenDataSoft) is a data marketplace solution that allows organizations to centralize, share, and distribute data products securely and interactively. It is widely used in Switzerland for managing OpenData repositories, including data.bs.ch, the official OpenData portal of the City of Basel. This application is designed to work seamlessly with data.bs.ch, but it can be easily adapted to any other ODS repository.

The **Fast OGD Data Caching Application** is designed to accelerate access to Open Government Data (OGD) from **data.bs.ch** by creating **local and cloud-based data caches**. Since direct access to large datasets via ODS is slow, this application provides **efficient alternatives** for storing and querying OGD datasets.

By enabling **local caching, Azure Blob storage, and Snowflake integration**, the app ensures fast access to structured data, optimizing costs based on dataset size and application needs.

---

## **🔹 Key Features**

### **1️⃣ Download ODS Dataset**
📥 **Functionality:**  
- Downloads data from **data.bs.ch (OGD OpenData repository)**.
- Saves datasets as **Parquet files** on the local machine for efficient storage and retrieval. You need to copy these parquet files to and deploy them with your applications. However you will have to include a mechanism to keep your data up to date. Also, these data updates will be lost when you restart your application. 
  
📌 **Use Case:**  
Ideal for **small to medium datasets** that need repeated access without querying ODS directly.

---

### **2️⃣ Upload Parquet Files to Azure**
☁️ **Functionality:**  
- Uploads **local Parquet files** to an **Azure Data Blob**.
- Provides **low-cost** cloud storage for datasets up to **500MB**.

📌 **Use Case:**  
Best for **medium-sized datasets** that need cloud accessibility while keeping costs low.

---

### **3️⃣ Upload Parquet Files to Snowflake**
❄️ **Functionality:**  
- Uploads **local Parquet files** to a **Snowflake table**.
- Stores large datasets in Snowflake for **efficient structured querying**.

📌 **Use Case:**  
Used for **large datasets** when local storage or Azure downloads are **too slow or impractical**.

---

### **4️⃣ Load Remote Data from Azure**
🔄 **Functionality:**  
- Loads and displays **structured data** stored in **Azure Blob Storage**.
- Downloads **entire blobs** to the application for use.

📌 **Use Case:**  
Best for **datasets up to 500MB**, ensuring fast retrieval while keeping storage costs minimal.

---

### **5️⃣ Query Snowflake Data**
🧐 **Functionality:**  
- Runs **SQL queries** on **Snowflake-stored datasets**.
- Enables **complex filtering, aggregation, and analysis** directly on Snowflake.

📌 **Use Case:**  
Essential for **very large datasets**, where downloading them entirely is **too slow or storage-intensive**.

---

## **⚖️ Cost & Performance Optimization Strategy**
| **Storage Option** | **Best for Dataset Size** | **Performance** | **Cost Consideration** |
|------------------|---------------------|-------------|-----------------|
| **Local Parquet Files** | Small to Medium | ⚡ Fastest | 💰 Free |
| **Azure Blob Storage** | Up to 500MB | ⚡ Fast | 💲 Low-cost |
| **Snowflake Tables** | Large Datasets | ⚡⚡ Fast (SQL-based) | 💲💲 Compute + Storage |

🔹 **For small datasets**, local **Parquet caching** ensures **instant access**.  
🔹 **For medium datasets**, **Azure Blob Storage** is the best balance between **cost and speed**.  
🔹 **For large datasets**, **Snowflake** provides **powerful SQL-based querying**, but costs include **compute time**.  

---

## **🚀 Why Use This App?**
✅ **Eliminates slow direct access to ODS for large datasets**  
✅ **Provides multiple storage options (Local, Azure, Snowflake) based on dataset size**  
✅ **Optimizes cost by using the cheapest storage for each use case**  
✅ **Supports fast SQL querying for structured data in Snowflake**  
✅ **Allows flexible data migration between local, cloud, and Snowflake storage**

---

This application is **ideal for organizations and developers** working with **data.bs.ch** datasets who need **fast, cost-efficient access** to large OGD datasets. 🚀
    """,
    "title_download_ods": "Download ODS Data",
    "info_download_ods": "Seletct files to be downloaded from the ODS repository an saved to the local disk, then click the download button.",
}
