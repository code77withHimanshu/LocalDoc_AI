package com.localdocai.backend.controller;

import com.localdocai.backend.dto.DocumentsResponse;
import com.localdocai.backend.service.AiServiceClient;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(DocumentController.class)
class DocumentControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private AiServiceClient aiServiceClient;

    @Test
    void listsDocumentsFromAiService() throws Exception {
        DocumentsResponse response = new DocumentsResponse();
        response.setDocuments(List.of("sample.pdf"));
        when(aiServiceClient.listDocuments()).thenReturn(response);

        mockMvc.perform(get("/api/documents"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.documents[0]").value("sample.pdf"));
    }
}
