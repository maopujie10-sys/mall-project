<template>
  <div class="table-list">
    <el-card>
      <el-form ref="searchForm" :model="form" inline>
        <el-form-item :label="$t('会员昵称:')" prop="order_name">

          <el-input v-model="form.userName" :placeholder="$t('请输入会员昵称')"></el-input>

        </el-form-item>
        <el-form-item :label="$t('评价:')" prop="time">

          <el-select v-model="form.evaluationType" :placeholder="$t('请选择')">

            <el-option v-for="item in status_options" :key="item.value" :label="item.label" :value="item.value">
            </el-option>

          </el-select>

        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">{{ $t('查询') }}</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="reset">{{ $t('重置') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <el-card>
      <el-table ref="multipleTable" :data="tableData" border stripe style="width: 100%">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column :label="$t('商品名称')" align="center">
          <template slot-scope="scope">
            {{ scope.row.goodsVo.name }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('会员昵称')" align="center" prop="userName"></el-table-column>
        <el-table-column :label="$t('评价')" align="center" prop="content">
          <template slot-scope="scope">
            <el-tag v-if="scope.row.evaluationType == 1" type="success">{{ $t('好评') }}</el-tag>
            <el-tag v-else-if="scope.row.evaluationType == 2" type="warning">{{ $t('中评') }}</el-tag>
            <el-tag v-else type="danger">{{ $t('差评') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('评分')" align="center" prop="rating"></el-table-column>
        <el-table-column :label="$t('评价内容')" align="center" prop="content">
          <template slot-scope="scope">
            <el-tooltip v-if="scope.row.content" :content="scope.row.content" placement="top">
              <div class="ellipsis">
                {{ scope.row.content }}
              </div>
            </el-tooltip>
            <span v-else style="color: #cccccc">{{ $t('用户未发表评论') }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('评价图片')" align="center" prop="content">
          <template slot-scope="scope">
            <!--    查看图片        -->
            <el-button v-if="countImage(scope.row)" size="mini" type="primary" @click="showImage(scope.row)">
              {{ $t('查看图片') }}
            </el-button>
            <span v-else>--</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('评论时间')" align="center" prop="commentTime">
          <template slot-scope="scope">
            {{ scope.row.evaluationTime | formatZoneDate }}
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 20px; text-align: center">
        <el-pagination
            :current-page.sync="pageNum"
            :page-size="pageSize"
            :total="totalElements"
            background
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange">
        </el-pagination>
      </div>
    </el-card>
    <el-dialog :title="$t('查看评论图片')" :visible.sync="showImageDialog">
      <el-carousel :interval="4000" arrow="always" indicator-position="outside" height="440px">
        <el-carousel-item v-for="(item, index) in showImageList" :key="index">
          <img :src="item" alt="img" class="carousel-item-img"/>
        </el-carousel-item>
      </el-carousel>
    </el-dialog>
  </div>
</template>

<script>
import {pinglun_list_post} from "@/api/user";

export default {
  name: "table-list",
  mounted() {
    this.getAllData();
  },
  data() {
    return {
      form: {
        pageSize: 10,
        pageNum: 1,
        userName: undefined,
        evaluationType: undefined
      },
      currentPage: 0,
      status_options: [
        {
          label: this.$t('全部'),
          value: undefined,
        },
        {
          label: this.$t('好评'),
          value: "1",
        },
        {
          label: this.$t('中评'),
          value: "2",
        },
        {
          label: this.$t('差评'),
          value: "3",
        },
      ],
      tableData: [],
      carouselIndex: 0,
      pageNum: 1,
      pageSize: 10,
      totalElements: 0,
      showImageDialog: false,
      showImageList: []
    };
  },
  methods: {
    countImage(row) {
      let arr = []
      for (let i = 1; i < 10; i++) {
        let item = row['imgUrl' + i]
        if (item) {
          arr.push(row['imgUrl' + i])
        }
      }
      return arr.length > 0
    },
    showImage(row) {
      this.showImageList = []
      for (let i = 1; i < 10; i++) {
        let item = row['imgUrl' + i]
        if (item) {
          this.showImageList.push(row['imgUrl' + i])
        }
      }
      this.showImageDialog = true
    },
    // TODO: 搜索请求
    search() {
      console.log(this.form);
      this.getAllData();
    },
    // TODO: 重置搜索条件并且请求
    reset() {
      this.form = {
        userName: undefined,
        evaluationType: undefined
      }
      this.$refs.searchForm.resetFields();
      this.getAllData();
    },
    // TODO: 每页几条,去请求获取数据
    handleSizeChange(val) {
      console.log(`每页 ${val} 条`);
      this.pageSize = val;
      this.getAllData();
    },
    // TODO: 当前第几页,去请求获取数据
    handleCurrentChange(val) {
      console.log(`当前页: ${val}`);
      this.getAllData();
    },
    // TODO: 获取列表数据
    getAllData() {
      console.log("请求获取列表数据");
      this.form["pageNum"] = this.pageNum;
      this.form["pageSize"] = this.pageSize;
      pinglun_list_post(this.form).then(res => {

        this.tableData = res.data.pageList
        this.totalElements = res.data.pageInfo.totalElements
      }).catch(function (err) {

      })
    },
  },
};
</script>

<style lang="scss" scoped>
//轮播图
::v-deep {
  .el-carousel {
    width: 100%;

    .el-carousel__container {
      height: auto;
      width: auto;
    }

    .carousel-item-img {
      height: 100%;
      display: block;
      margin: auto;
    }

    .el-carousel__indicators--horizontal {
      background: rgba(0, 0, 0, 0.1);
    }
  }
}

.table-list {
  width: 100%;
  height: 100%;

  .search {
    padding: 20px 20px 0px 20px;
    background-color: #fff;
    margin-bottom: 10px;
    border-radius: 10px;
  }

  .table {
    padding: 20px;
    background-color: #fff;
    border-radius: 10px;

    ::v-deep .el-table__header-wrapper thead tr th {
    }
  }

  .detail {
    border: 1px solid #ccc;
    border-radius: 3px;
    margin-bottom: 20px;

    .header {
      line-height: 40px;
      padding-left: 10px;
      border-bottom: 1px solid #ccc;
    }

    .main-price {
      .item {
        display: flex;
        line-height: 30px;
        margin: 10px;
        justify-content: space-between;
        font-size: 16px;
        font-weight: 800;

        .name {
          font-weight: 800;
          font-size: 16px;
        }
      }

      .top {
        border-top: 1px solid #ccc;
        padding-top: 10px;
      }
    }
  }

  .btn {
    text-align: left;
    margin-bottom: 15px;

    ::v-deep .el-button {
      color: #fff;
      // background-color: rgb(22, 155, 213);
    }
  }

  .order-top {
    border: 1px solid #ccc;
    border-radius: 3px;
    margin-bottom: 20px;

    .header {
      line-height: 40px;
      padding-left: 10px;
      border-bottom: 1px solid #ccc;
    }

    .main {
      .border {
        border-top: 1px solid #ccc;
      }

      &-content {
        display: flex;
        justify-content: space-between;
        margin: 0 10px;

        .left {
          width: 40%;

          .item {
            display: flex;
            line-height: 30px;
            margin: 10px;
            justify-content: space-between;
            font-size: 16px;
            font-weight: 800;
          }
        }

        .right {
          width: 40%;

          .item {
            display: flex;
            line-height: 30px;
            margin: 10px;
            justify-content: space-between;
            font-size: 16px;
            font-weight: 800;
          }
        }
      }
    }
  }

  .order-bottom {
    display: flex;
    justify-content: space-between;

    .content-left,
    .content-right {
      border: 1px solid #ccc;
      border-radius: 3px;
      margin-bottom: 20px;

      .header {
        line-height: 40px;
        padding-left: 10px;
        border-bottom: 1px solid #ccc;
      }
    }

    .content-left {
      width: calc(70% - 20px);
    }

    .content-right {
      width: 30%;

      .item {
        display: flex;
        line-height: 30px;
        margin: 10px;
        justify-content: space-between;
        font-size: 16px;
        font-weight: 800;

        .name {
          font-weight: 800;
          font-size: 16px;
        }
      }

      .top {
        border-top: 1px solid #ccc;
        padding-top: 10px;
      }
    }
  }

  //::v-deep .el-dialog__header {
  //  background-color: #ccc;
  //  font-weight: 700;
  //  color: #000000;
  //}
  //::v-deep .el-dialog__headerbtn .el-dialog__close {
  //  color: #333;
  //}
}

.up {
  text-align: right;
  display: inline-block;
  width: 60px;
  margin-left: -20px;
  margin-right: 10px;
}

::v-deep {
  .date .el-date-editor {
    width: 100%;
  }

  .el-carousel__arrow {
    background: rgba(0, 0, 0, 0.5);
    font-size: 16px;
    font-weight: bold;
    box-shadow: 0 0 4px rgba(255, 255, 255, 0.5);

    &:hover {
      background: rgba(0, 0, 0, 0.7);
    }
  }
}
</style>
