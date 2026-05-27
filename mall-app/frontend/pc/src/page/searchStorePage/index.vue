<template>
  <div>
    <EsHeaderView @reload="pageInit" />
    <div class="app-container">
      <div v-if="currentLang === 'en'" class="tips-content">
        Find {{ listData.length }} <span>"{{ keyword }}"</span> related stores for you
      </div>
      <div v-else class="tips-content">{{ $t('message.home.storeSeachTips1') }} <span>"{{ keyword }}"</span> {{ $t('message.home.storeSeachTips2') }} {{ listData.length }} {{ $t('message.home.storeSeachTips3') }}</div>
      
      <div v-loading="pageLoading" class="store-content-main">
        <div v-if="listData.length" class="content">
          <div v-for="item in listData" :key="item.id" class="item">
            <EsStore :item="item" />
          </div>
        </div>
        <el-empty v-if="!listData.length && !pageLoading" :description="$t('message.home.noData')"></el-empty>
      </div>
    </div>
    <EsFooterView />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { SearchApi } from "@/api"
import EsStore from '@/components/store'
export default {
  name: 'SearchStore',
  components: {
    EsStore
  },
  data() {
    return {
      keyword: '',
      pageLoading: true,
      listData: []
    }
  },
  computed: {
    ...mapGetters({
      currentLang: "currentLang"
    }),
  },
  mounted () {
    this.$nextTick(() => {
      this.pageInit()
    })
  },
  methods: {
    pageInit() {
      const { k } = this.$route.query
      console.log('this.$route ->', this.$route);
     
      if (k) {
        if (k.indexOf('&') !== -1){
          const val  = JSON.parse(k)
          this.keyword =  String(encodeURIComponent(val)).trim()
        }else{
          const val  = JSON.parse(k)
          this.keyword = String(val).trim()
        }
       this.getData()
      } else {
        this.$router.push('/')
      }
    },
    getData() {
      this.pageLoading = true
     
      SearchApi({
        keyword:this.keyword
      }).then(res => {
        const { sellerList } = res.data
        this.pageLoading = false
        this.listData = sellerList || []
      }).catch(() => {
        this.pageLoading = false
      })
    }
  }
}
</script>

<style scoped lang="scss">
.app-container {
  width: 1200px;
}
.tips-content {
  > span {
    color: var(--color-main);
  }
}

.store-content-main {
  min-height: 300px;
  margin-top: 20px;
  > .content {
    overflow: hidden;
    > .item {
      width: 30%;
      float: left;
      margin-right: 5%;
      margin-bottom: 20px;
      &:nth-child(3n) {
        margin-right: 0;
      }
      /deep/ .stroe-top-title {
        h2 {
          overflow:hidden;
          white-space: nowrap;
          text-overflow: ellipsis;
          -o-text-overflow: ellipsis;
          width: 230px;
        }
      }
    }
  }
}
</style>
