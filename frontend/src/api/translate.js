import { agentApi } from './index'
export function translateProduct(content, target_lang='en') { return agentApi.post('/agent/translate/translate', {content, target_lang}) }
export function publishProduct(content, target_langs=['en','ja','ko'], platforms=['shopify','etsy']) { return agentApi.post('/agent/translate/publish', {content, target_langs, platforms}) }
export function getLanguages() { return agentApi.get('/agent/translate/languages') }
export function getPlatforms() { return agentApi.get('/agent/translate/platforms') }
export function getPublishHistory() { return agentApi.get('/agent/translate/history') }
