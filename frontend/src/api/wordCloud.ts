import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface WordCloudRequest {
  words: string[];
}

export interface WordCloudResponse {
  words: Array<{
    text: string;
    value: number;
  }>;
}

export const wordCloudAPI = {
  async generateWords(): Promise<string[]> {
    const response = await axios.get(`${API_BASE_URL}/wordcloud/generate`);
    return response.data.words;
  },

  async processWords(words: string[]): Promise<WordCloudResponse> {
    const response = await axios.post(`${API_BASE_URL}/wordcloud/process`, { words });
    return response.data;
  },
};
