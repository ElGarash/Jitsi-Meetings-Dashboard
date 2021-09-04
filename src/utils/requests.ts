import axios from 'axios';
import { accessTokenStore } from '../utils/stores';

let token;

accessTokenStore.subscribe((value) => (token = value));

axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

const baseUrl = 'https://meetingtriggerapp.azurewebsites.net/dashboard';

export const deleteResource = (id, type) => {
	return axios.delete(`${baseUrl}/${type}/${id}`);
};

export const patchResource = (id, type, requestBody) => {
	return axios.patch(`${baseUrl}/${type}/${id}`, requestBody);
};

export const postResource = (type, requestBody) => {
	return axios.post(`${baseUrl}/${type}`, requestBody);
};

export const getActiveRooms = () => {
	const request = axios.get(`${baseUrl}/meetings`);
	return request
		.then((response) => response.data)
		.then((responseData) => responseData.activeMeetings);
};
