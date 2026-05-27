<template>
    <div>
        <EsHeaderView @reload="pageInit"/>
        <div class="app-container">
            <!-- <div> -->
            <EsSortView @sort="sortEvent" :hide-new="false" v-if="isSort" />
            <!-- </div> -->
            <div v-loading="pageLoading" class="store-content-main">
                <div v-if="listData.length" class="content">
                    <div v-for="item in listData" :key="item.id" class="item">
                        <EsProductView :item="item" />
                    </div>
                </div>
                <div v-if="listData.length" class="content-pagination">
                    <el-pagination background layout="prev, pager, next" class="es-pagination" :page-size="pageSize"
                        :current-page="pageNum" :total="total" @current-change="currentChange" />
                </div>
                <el-empty v-if="!listData.length && !pageLoading" :description="$t('message.home.noData')"></el-empty>
            </div>
        </div>
        <EsFooterView />
    </div>
</template>

<script>
import { SearchResultListApi } from "@/api";
import EsProductView from "@/components/product";
import EsSortView from "@/page/commodityPage/sort.vue";
export default {
    name: "SearchGoods",
    components: {
        EsProductView,
        EsSortView,
    },
    data() {
        return {
            keyword: "",
            pageLoading: true,
            pageNum: 1,
            pageSize: 12,
            total: 0,
            listData: [],
            isSort: true,
            isLoad: false,
            params: {},
            key:''
        };
    },
    activated() {
        // console.log('this.$route.query ->', this.$route.query);
        //   this.isSort = true
        const { k } = this.$route.query;
        // if (!k) {
        //   this.$router.push("/");
        // } else {
        this.keyword = k
        this.$nextTick(() => {
        this.pageInit();
        });
        // }
    },
    methods: {
        sortEvent(params) {
            console.log('params ->', params);
            this.params = params;
            this.pageNum = 1;
            this.getData(params);
        },
        pageInit() {
            if (this.keyword) {
                if(!this.isLoad) {
                    this.getData();
                    this.isSort = false
                    setTimeout(() => {
                        this.isSort = true
                    }, 100);
                }
            } else {                
                this.$router.push("/");
            }
        },
        getData(params = {}) {
            this.pageLoading = true;
            if (this.keyword) {
                if (this.keyword.indexOf('&') !== -1 || this.keyword.indexOf('#') !== -1){
                const val  = JSON.parse(this.keyword)
                this.key =  String(encodeURIComponent(val)).trim()
                }else{
                const val  = JSON.parse(this.keyword)
                console.log('val ->', val);
                this.key = String(val).trim()
                }
                SearchResultListApi({
                    keyword: this.key,
                    pageNum: this.pageNum,
                    pageSize: this.pageSize,
                })
                    .then((res) => {
                        const { pageList, pageInfo } = res.data;
                        this.total = pageInfo.totalElements;
                        console.log('pageList.data ->', pageList.data);
                        if (pageList.length) {
                            this.listData = pageList;
                        } else {
                            this.listData = [];
                        }
                        this.pageLoading = false;
                    })
                    .catch(() => {
                        this.pageLoading = false;
                    });
            }
        },
        currentChange(page) {
            this.pageNum = page;
            this.getData(this.params);
        },
    },
    // deactivated() {
    //       this.isSort = false;
    // },
    watch: {
        $route(to, from) {
            // console.log(`from----------111 ::->`, from);
            this.isLoad = from.path === '/productDetails'
            // console.log(' this.isLoad->', this.isLoad);
            // this.pageInit();
        },
    },
};
</script>

<style scoped lang="scss">
.app-container {
    width: 1200px;
}

.tips-content {
    >span {
        color: var(--color-main);
    }
}

.store-content-main {
    min-height: 300px;
    margin-bottom: 40px;

    >.content {
        overflow: hidden;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(188px, 165px));
        grid-column-gap: 14px;
        grid-row-gap: 20px;
        align-content: center;
        padding: 40px 0;
        >.item {

            &:nth-child(6n) {
                margin-right: 0;
            }
        }
    }
}

.content-pagination {
    width: 100%;
    display: flex;
    justify-content: center;
    margin-top: 20px;
}
</style>
