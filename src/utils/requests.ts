import axios from 'axios';
import { accessTokenStore } from '../utils/stores';

let token;

accessTokenStore.subscribe((value) => (token = value));

axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

const baseUrl = 'https://meetingtriggerapp.azurewebsites.net/dashboard';

const deleteResource = (id, type) => {
	const request = axios.delete(`${baseUrl}/${type}/${id}`);
	return request.then((response) => response);
};

const patchResource = (id, type, requestBody) => {
	const request = axios.patch(`${baseUrl}/${type}/${id}`, requestBody);
	return request.then((response) => response);
};

const postResource = (type, requestBody) => {
	const request = axios.post(`${baseUrl}/${type}`, requestBody);
	return request.then((response) => response);
};

const requests = { patchResource, deleteResource, postResource };
export default requests;
