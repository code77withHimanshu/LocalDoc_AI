package com.localdocai.backend.dto;

import java.util.List;

public class DocumentsResponse {
    private List<String> documents;

    public List<String> getDocuments() {
        return documents;
    }

    public void setDocuments(List<String> documents) {
        this.documents = documents;
    }
}
