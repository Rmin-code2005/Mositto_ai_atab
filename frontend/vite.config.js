import {defineConfig} from 'vite';
export default defineConfig({server:{proxy:{'/people':'http://127.0.0.1:8000','/sessions':'http://127.0.0.1:8000','/health':'http://127.0.0.1:8000'}},test:{environment:'jsdom'}});
