import axios from "axios";

const api = axios.create({ baseURL: process.env.NEXT_PUBLIC_API_BASE || "/api" });

export async function getAuthUrl() {
  const { data } = await api.get("/auth/yahoo/login");
  return data.auth_url as string;
}

export async function getDraftRecs(leagueKey: string) {
  const { data } = await api.get(`/draft/recommendations`, { params: { leagueKey } });
  return data;
}

export default api;