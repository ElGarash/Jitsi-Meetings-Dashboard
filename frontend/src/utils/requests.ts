import axios from 'axios';

const baseUrl = 'https://meetingtriggerapp.azurewebsites.net/dashboard';

export const deleteResource = (id, type, accessToken) => {
  return axios.delete(`${baseUrl}/${type}/${id}`, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
};

export const patchResource = (id, type, requestBody, accessToken) => {
  return axios.patch(`${baseUrl}/${type}/${id}`, requestBody, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
};

export const postResource = (type, requestBody, accessToken) => {
  return axios.post(`${baseUrl}/${type}`, requestBody, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
};

export const getActiveRooms = (accessToken) => {
  const request = axios.get(`${baseUrl}/meetings`, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  return request
    .then((response) => response.data)
    .then((responseData) => responseData.activeMeetings);
};
