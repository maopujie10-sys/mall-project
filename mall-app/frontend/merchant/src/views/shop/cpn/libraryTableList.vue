<template>
  <div class="table-list">
    <el-card>
      <el-form ref="searchForm" :model="form" inline>
        <el-form-item :label="$t('商品名称:')" prop="order_name">

          <el-input v-model="form.name" :placeholder="$t('请输入商品名称')"></el-input>

        </el-form-item>
        <el-form-item :label="$t('商品ID:')" prop="order_name">

          <el-input v-model="form.id" :placeholder="$t('请输入商品ID')"></el-input>

        </el-form-item>
        <!--        <el-form-item :label="$t('商品分类:')" prop="order_status">-->

        <!--          <el-select v-model="form.categoryId" :placeholder="$t('请选择')">-->

        <!--            <el-option v-for="item in categoryList" :key="item.categoryId" :label="item.name" :value="item.categoryId">-->
        <!--            </el-option>-->

        <!--          </el-select>-->

        <!--        </el-form-item>-->
        <el-form-item :label="$t('商品分类:')" prop="order_status">
          <GoodsCategory v-model="form.categoryId" :all="true"/>
        </el-form-item>
        <!--                      <el-form-item :label="$t('二级分类:')" prop="time">-->

        <!--              <el-select :placeholder="$t('请选择')" v-model="form.order_status">-->

        <!--                          <el-option v-for="item in status_options" :key="item.value" :label="item.label" :value="item.value">-->
        <!--                          </el-option>-->

        <!--                        </el-select>-->

        <!--                      </el-form-item>-->
        <el-form-item>
          <el-button type="primary" @click="search">{{ $t('查询') }}</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="reset">{{ $t('重置') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <!--    {{multipleSelection}}-->
    <el-card>
      <div class="btn">
        <el-button type="primary" @click="showBatch2('批量添加')">{{ $t('添加') }}</el-button>
      </div>
      <el-table ref="multipleTable" :data="tableData" border stripe style="width: 100%"
                @selection-change="handleSelectionChange" :row-key="getRowKey">
        <el-table-column type="selection" width="55" :reserve-selection="true"></el-table-column>
        <el-table-column :label="$t('商品ID')" align="center" prop="id"></el-table-column>
        <el-table-column :label="$t('封面图')" align="center" prop="order_no">

          <template slot-scope="scope">
            <el-image :src="scope.row.imgUrl1"/>
          </template>

        </el-table-column>
        <el-table-column :label="$t('商品名称')" align="center" prop="name" min-width="360"></el-table-column>
        <el-table-column :label="$t('分类')" align="center" prop="categoryName"></el-table-column>
        <el-table-column :label="$t('二级分类')" align="center" prop="secondaryCategoryName">
        </el-table-column>
        <el-table-column :label="$t('采购价格')" align="center" prop="change_money">
          <template slot-scope="scope">
            <div :style="{ color: scope.row.systemPrice > 0 ? '#409EFF' : '#F56C6C' }">
              <FormatNumberShow :data="scope.row.systemPrice" :currency="true"/>
            </div>
          </template>
        </el-table-column>
        <!--        <el-table-column-->
        <!--          label="库存"-->
        <!--          align="center"-->
        <!--          prop="lastAmount"-->
        <!--        ></el-table-column>-->
        <el-table-column :label="$t('操作')" align="center" min-width="160">
          <template slot-scope="scope">
            <el-button @click="showBatch(scope.row.id)">{{ $t('添加') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 20px; text-align: center">
        <!--        <el-pagination background @size-change="handleSizeChange" @current-change="handleCurrentChange"-->
        <!--                       :current-page="currentPage" :page-sizes="[10, 20, 50, 100]" :page-size="pageSize"-->
        <!--                       layout="total, sizes, prev, pager, next, jumper" :total="tableData.length">-->
        <!--        </el-pagination>-->
        <el-pagination
            :current-page.sync="form.pageNum"
            :page-size="form.pageSize"
            :total="form.totalElements"
            background
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange">
        </el-pagination>
      </div>
    </el-card>

    <EditCommodity ref="editCommodity" @submitCommodity="submitCommodity"/>

  </div>
</template>

<script>
import {seller_info_action_post, shangpinku_list_post, tianjia_post} from "@/api/user";
import Toast from "@/utils/toast";
import {getCategory} from "@/api/goods";
import EditCommodity from "@/components/EditCommodity";
import FormatNumberShow from "@/components/FormatNumberShow/index.vue";
import GoodsCategory from "@/components/GoodsCategory/index.vue";

export default {
  name: "table-list",
  mounted() {
    this.getAllData();
    this.seller_info_action();
  },
  components: {
    FormatNumberShow,
    EditCommodity,
    GoodsCategory
  },
  data() {
    return {
      selectTableIds: [], //当前选中的商品
      form: {
        categoryId: undefined,
        name: undefined,
        id: undefined,
        discount: undefined,
        pageNum: 1,
        pageSize: 10,
        totalElements: 0
      },
      editTitle: [],
      count: 0,
      editVisible: false,
      currentPage: 0,
      status_options: [
        {
          label: this.$t('全部'),
          value: "all",
        },
        {
          label: this.$t('手机'),
          value: "add",
        },
        {
          label: this.$t('电脑'),
          value: "remove",
        },
        {
          label: this.$t('相机'),
          value: "camera",
        },
      ],
      order_options: [
        {
          label: this.$t('全部'),
          value: "all",
        },
        {
          label: this.$t('服装'),
          value: "add",
        },
        {
          label: this.$t('数码'),
          value: "remove",
        },
      ],
      tableData: [],
      goodsIds: '',
      pageSize: 10,
      multipleSelection: [],
      info: {},
      categoryList: [],
      selectIdObj: {//选中的id

      }
    };
  },
  methods: {
    getRowKey(row) {
      return row.id;
    },
    selectTableIdsChange(val) {
      this.selectTableIds = val
    },
    filtersNumber(e, type) {
      if (e > 100) {
        this.form[type] = 100
      }
    },
    seller_info_action() {
      seller_info_action_post({}).then((e) => {
        console.log(e)
        this.info = e.data
        this.fenlei_post_fu()
      }).catch((e) => {
      })
    },
    fenlei_post_fu() {
      getCategory({sellerId: this.info.id, pageSize: 100}).then((e) => {
        console.log(e)
        this.categoryList = e.data.pageList
      }).catch((e) => {
      })
    },
    handleSelectionChange(val) {
      this.multipleSelection = val;
    },
    submitCommodity(e) {
      // if (['JustShop'].includes(projectTitle) && !this.$store.getters.userInfo.phone) {
      //   Toast.fail(this.$t('请绑定手机号'));
      //   return
      // }
      let data = {
        goodsIds: this.goodsIds,
        profit: e.profitRatio ? (e.profitRatio / 100).toFloor(2) : 0,
        discount: e.discountRatio ? (e.discountRatio / 100).toFloor(2) : undefined,
        startTime: e.discountStartTime,
        endTime: e.discountEndTime,
      }
      if (e.discountStartTime && e.discountEndTime && !e.discountRatio) {
        data.discount = 0
      } else {
        data.discount = e.discountRatio / 100
      }

      tianjia_post(data).then(res => {
        Toast.success(this.$t('添加成功'));
        this.$refs.editCommodity.changeEditVisible(false)
        this.editTitle = []
        this.$refs.multipleTable.clearSelection()
        this.getAllData();
      })
    },
    showBatch(id) {
      this.count = this.$refs.multipleTable.selection.length
      this.goodsIds = [id].join(',')
      // this.form = {
      //   categoryId: undefined,
      //   name: undefined,
      //   id: undefined,
      //   discount: undefined,
      // }
      this.$refs.editCommodity.changeEditVisible(true)
      this.$refs.editCommodity.changeUpdateInfo();
      this.$refs.editCommodity.reset();
    },
    showBatch2(title) {
      this.count = this.$refs.multipleTable.selection.length
      this.editTitle = []
      if (this.multipleSelection.length == 0) {
        Toast(this.$t('请选择商品'));
        return;
      }
      for (let i = 0; i < this.multipleSelection.length; i++) {
        this.editTitle.push(this.multipleSelection[i].id)
      }
      this.goodsIds = this.editTitle.join(',')
      this.editVisible = true
      this.$refs.editCommodity.changeEditVisible(true)
      this.$refs.editCommodity.changeUpdateInfo()
      this.$refs.editCommodity.reset();
    },
    // TODO: 搜索请求
    search() {
      console.log(this.form);
      this.form.totalElements = 0
      this.getAllData();
    },
    // TODO: 重置搜索条件并且请求
    reset() {
      // this.$refs.searchForm.resetFields(); // 重置表单
      this.form = {
        categoryId: undefined,
        isShelf: undefined,
        name: undefined,
        id: undefined,
        pageNum: 1,
        pageSize: 10,
        totalElements: 0
      }
      this.getAllData();
    },
    // TODO: 每页几条,去请求获取数据
    handleSizeChange(val) {
      console.log(`每页 ${val} 条`);
      this.form.pageSize = val
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
      let data = {...this.form}
      data.categoryId = data.categoryId ? data.categoryId[data.categoryId.length - 1] : undefined
      shangpinku_list_post(data).then(res => {
        this.tableData = res.data.pageList
        this.form.totalElements = res.data.pageInfo.totalElements
        this.$nextTick(() => {//查找当前页选中的数据
          this.tableData.forEach((item) => {
            if (this.selectIdObj[item.id]) {
              this.$refs.multipleTable.toggleRowSelection(item);
            }
          });
        })

        //2023-2-22 add 3330 【商家PC】上架商品后店铺认证的框还在
        seller_info_action_post({}).then((res) => {
          this.storeName = res.data?.name
          this.$store.commit('user/CHANGE_MERCHANT_INFO', res.data)
        })
        //end
      }).catch(function (err) {

      })
    },
  },
};
</script>

<style lang="scss" scoped>
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

  ::v-deep .el-dialog__header {
    //background-color: #ccc;
    //font-weight: 700;
    //color: #000000;
  }

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

::v-deep .date .el-date-editor {
  width: 100%;
}
</style>
