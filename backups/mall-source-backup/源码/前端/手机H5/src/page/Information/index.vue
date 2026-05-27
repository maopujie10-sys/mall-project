<template>
  <div class="page-content">
    <van-nav-bar safe-area-inset-top
        fixed
        :title="$t('消息')"
        left-arrow
        @click-left="() => $router.back()"
    />
    <div style="width: 100%;" class="h46"></div>
    <div class="msg-content">
      <router-link to="/customerServiceIndex">
        <div class="msg-item">
          <div class="avatar">
            <img :src="images.service" alt=""/>
          </div>
          <div class="info">
            <h3 class="service">{{ $t('客服中心') }}</h3>
          </div>
        </div>
      </router-link>
      <!-- <div class="msg-item">
        <div class="avatar">
          <img :src="images.avatar" alt="" />
        </div>
        <div class="info">
          <h3>DEMO</h3>
          <p>My bf like</p>
        </div>
        <div class="tips">
          <p class="num">5</p>
          <p class="time">刚刚</p>
        </div>
      </div> -->
    </div>
    <!-- <van-pull-refresh class="pull-content" v-model="refreshing" @refresh="onRefresh" :pulling-text="$t('下拉即可刷新')" :loosing-text="$t('释放即可刷新')" :loading-text="$t('加载中')">
      <van-list
        v-model="loading"
        :finished="finished"
        :finished-text="list.length ? $t('没有更多了') : ''"
        @load="onLoad"
      >
        <div v-if="list.length" class="list-content">
          消息中心
        </div>
        <van-empty v-else :description="$t('暂无数据')" />
      </van-list>
    </van-pull-refresh> -->
  </div>
</template>

<script>
import {NavBar, List, PullRefresh, Empty} from 'vant';
import {isLogin} from '@/utils/utis'

export default {
  name: 'Information',
  components: {
    [NavBar.name]: NavBar,
    [List.name]: List,
    [Empty.name]: Empty,
    [PullRefresh.name]: PullRefresh
  },
  data() {
    return {
      list: [],
      loading: false,
      finished: false,
      refreshing: false,
      page_no: 0,
      images: {
        avatar: require('@/assets/image/index/avatar1.png'),
        service: require('@/assets/image/index/live.png')
      }
    }
  },
  created() {
    if (!isLogin()) {
      this.$router.push('/')
    }
  },
  methods: {
    onRefresh() {
      // 清空列表数据
      this.finished = false;
      this.page_no = 0
      // 重新加载数据
      // 将 loading 设置为 true，表示处于加载状态
      this.loading = true;
      this.onLoad();
    },
    onLoad() {
      if (this.refreshing) {
        this.list = [];
        this.refreshing = false;
      }
      this.getTableList()
    },
    getTableList() {
      // this.page_no++
      // chongzhijilu_post({page_no:this.page_no}).then(res=>{
      //   console.log(res)
      //   for (let i = 0; i < res.length; i++) {
      //     this.list.push(res[i]);
      //   }
      //   console.log(this.list)
      //   this.loading = false;

      //   if (res.length==0) {
      //     this.finished = true;
      //   }
      // })
      this.loading = false;
      this.finished = true;
    }
  }
}
</script>

<style lang="scss" scoped>
.page-content {
  width: 100%;

  * {
    box-sizing: border-box;
  }

  .list-content {
    padding: 0 15px;
  }

  .pull-content {
    min-height: calc(100vh - 46px);
  }

  .msg-content {
    padding: 0 15px;

    .msg-item {
      display: flex;
      align-items: center;
      padding: 15px 0;
      border-bottom: 1px solid #eee;

      > .avatar {
        width: 45px;
        height: 45px;
        overflow: hidden;

        > img {
          width: 100%;
          height: auto;
        }
      }

      > .info {
        flex: 1;
        padding-left: 10px;
        padding-right: 15px;
        word-break: break-word;
        overflow: hidden;

        > h3 {
          font-size: 14px;
          font-weight: normal;
          color: #000 !important;

          &.service {
            font-weight: bold;
            font-size: 16px;
          }
        }

        > p {
          font-size: 12px;
          margin-top: 2px;
          text-overflow: ellipsis;
          overflow: hidden;
          white-space: nowrap;
        }
      }

      > .tips {
        width: 80px;

        > .num {
          float: right;
          vertical-align: baseline;
          background: #ff3e3e;
          border-radius: 50%;
          line-height: 15px;
          font-size: 12px;
          padding: 1px 5px;
          border-radius: 10px;
          color: #fff;

        }

        > .time {
          width: 80px;
          float: right;
          font-size: 10px;
          color: #999;
          text-align: end;
          margin-top: 3px;
        }
      }
    }
  }
}
</style>
