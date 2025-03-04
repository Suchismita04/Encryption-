import React, { useState } from "react";
import axios from "axios";
import "../Style/FileUploadStyle.css";

const FileUpload = () => {
  const [zipFile, setZipFile] = useState(null);
  const [zipPath, setZipPath] = useState("");
  const [message, setMessage] = useState("");
  const [password, setPassword] = useState("");

  const api = axios.create({
    baseURL: "/api", // Update to match your backend URL
    withCredentials: false,
  });

  const handleZipChange = (e) => {
    setZipFile(e.target.files[0]);
  };

  // Upload ZIP file
  const uploadZipFile = async () => {
    if (!zipFile) {
      setMessage("Please select a ZIP file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", zipFile);

    try {
      const response = await api.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setMessage("ZIP file uploaded successfully!");
      setZipPath(response.data.file_path);
    } catch (error) {
      setMessage("ZIP file upload failed.");
    }
  };

  // Start Dictionary Attack
  const startDictionaryAttack = async () => {
    if (!zipPath) {
      setMessage("Please upload a ZIP file first.");
      return;
    }

    setMessage("Performing dictionary attack...");
    try {
      const response = await api.post("/start-dictionary-attack", {
        file_path: zipPath,
      });

      if (response.data.password) {
        setPassword(response.data.password);
        setMessage(`Password found: ${response.data.password}`);
      } else {
        setMessage("Failed to find password in wordlist.");
      }
    } catch (error) {
      setMessage("Error performing dictionary attack.");
    }
  };

  return (
    <div className="container d-flex text-dark flex-column align-items-center mt-5" style={{ border: "1px solid #ccc", borderRadius: "8px", padding: "20px", backgroundColor: "#f9f9f9" }}>
      <h2 className="text-dark">ZIP File Password Cracker</h2>

      {/* ZIP Upload Section */}
      <label htmlFor="zipFile" className="form-label mt-3">Upload Encrypted ZIP File:</label>
      <input className="form-control" type="file" id="zipFile" onChange={handleZipChange} />
      <button className="btn btn-primary mt-2" onClick={uploadZipFile}>Upload ZIP</button>

      {/* Start Dictionary Attack */}
      <button className="btn btn-danger mt-4" onClick={startDictionaryAttack}>Start Dictionary Attack</button>

      {message && <p className="mt-3">{message}</p>}
      {password && <h3 className="text-success mt-3">Cracked Password: {password}</h3>}
    </div>
  );
};

export default FileUpload;
