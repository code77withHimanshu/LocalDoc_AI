package com.localdocai.backend.dto;

import java.util.List;

public class ChatResponse {
    private String answer;
    private List<Source> sources;

    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }

    public List<Source> getSources() {
        return sources;
    }

    public void setSources(List<Source> sources) {
        this.sources = sources;
    }
}
