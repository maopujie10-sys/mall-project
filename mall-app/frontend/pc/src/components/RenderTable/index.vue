<template>
    <el-table :data="data" v-bind="$attrs">
        <template v-for="(column, index) of columns">
            <!-- render -->
            <el-table-column v-if="column.render" v-bind="Object.assign({}, defaultColumnConfig, column)" :key="index">
                <template slot-scope="scope">
                    <extend :render="column.render" :params="scope"></extend>
                </template>
            </el-table-column>
            <!-- no render -->
            <el-table-column v-else v-bind="Object.assign({}, defaultColumnConfig, column)"
                :key="`${index}_object`"></el-table-column>
        </template>
    </el-table>
</template>
<script>
import extend from './extend.js'
export default {
    components: { extend },
    props: {
        data: {
            type: Array
        },
        columns: {
            type: Array
        },
        defaultColumnConfig: {
            type: Object
        }
    }
}
</script>