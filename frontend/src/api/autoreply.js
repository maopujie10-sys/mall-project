import { agentApi } from './index'
export function autoReply(message, user_id='') { return agentApi.post('/agent/autoreply/reply', {message, user_id}) }
export function getReplyRules() { return agentApi.get('/agent/autoreply/rules') }
export function createReplyRule(data) { return agentApi.post('/agent/autoreply/rules', data) }
export function deleteReplyRule(rule_id) { return agentApi.delete('/agent/autoreply/rules/'+rule_id) }
export function getConversations() { return agentApi.get('/agent/autoreply/conversations') }
export function getAutoReplyStats() { return agentApi.get('/agent/autoreply/stats') }
