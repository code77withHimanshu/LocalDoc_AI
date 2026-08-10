package com.localdocai.backend.dto;

public class UploadResponse {
    private String filename;
    private int chunks;

    public String getFilename() {
        return filename;
    }

    public void setFilename(String filename) {
        this.filename = filename;
    }

    public int getChunks() {
        return chunks;
    }

    public void setChunks(int chunks) {
        this.chunks = chunks;
    }
}
