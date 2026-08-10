package com.localdocai.backend.controller;

import com.localdocai.backend.dto.ChatResponse;
import com.localdocai.backend.service.AiServiceClient;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(ChatController.class)
class ChatControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private AiServiceClient aiServiceClient;

    @Test
    void returnsBadRequestForBlankQuestion() throws Exception {
        mockMvc.perform(post("/api/chat")
                        .contentType("application/json")
                        .content("{\"question\": \"  \"}"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void forwardsQuestionAndReturnsAiResponse() throws Exception {
        ChatResponse response = new ChatResponse();
        response.setAnswer("This document is about LocalDoc AI.");
        when(aiServiceClient.chat(any())).thenReturn(response);

        mockMvc.perform(post("/api/chat")
                        .contentType("application/json")
                        .content("{\"question\": \"What is this document about?\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.answer").value("This document is about LocalDoc AI."));
    }
}
