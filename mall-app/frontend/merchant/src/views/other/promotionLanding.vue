<template>
  <div class="merchandise">
    <div class="main">
      <div class="main-c">
        <el-form>
          <el-form-item>
            <p>{{ $t('店铺LOGO') }}</p>
            <el-upload :auto-upload="false" :limit="1" action="#" list-type="picture-card">
              <i slot="default" class="el-icon-plus"></i>
              <div slot="file" slot-scope="{ file }">
                <img :src="file.url" alt="" class="el-upload-list__item-thumbnail"/>
                <span class="el-upload-list__item-actions">
                                                                                <span
                                                                                    class="el-upload-list__item-preview"
                                                                                    @click="handlePictureCardPreview(file)">
                                                                                  <i class="el-icon-zoom-in"></i>
                                                                                </span>
                                                                                <span v-if="!disabled"
                                                                                      class="el-upload-list__item-delete"
                                                                                      @click="handleRemove(file)">
                                                                                  <i class="el-icon-delete"></i>
                                                                                </span>
                                                                              </span>
              </div>
            </el-upload>
            <p><span>{{ $t('建议尺寸') }}</span><span>200x200</span></p>
            <el-dialog :visible.sync="dialogVisible">
              <img :src="dialogImageUrl" alt="" width="100%"/>
            </el-dialog>
          </el-form-item>
          <el-form-item>
            <p>{{ $t('店铺名称') }}</p>
            <el-input :placeholder="$t('请填写店铺名称')"></el-input>
          </el-form-item>
          <el-form-item>
            <p>{{ $t('店铺地址') }}</p>
            <el-input :placeholder="$t('请填写店铺地址')"></el-input>
          </el-form-item>
          <el-form-item>
            <p>{{ $t('真实姓名') }}</p>
            <el-input :placeholder="$t('请填写真实姓名')"></el-input>
          </el-form-item>
          <el-form-item>
            <p>{{ $t('国籍') }}</p>
            <el-select v-model="value" :placeholder="$t('请选择')" style="width: 100%">

              <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value">
              </el-option>

            </el-select>
          </el-form-item>
          <el-form-item>
            <p>{{ $t('证件号码') }}</p>
            <el-input :placeholder="$t('请填写证件/护照号码')"></el-input>
          </el-form-item>
          <el-form-item>
            <p>{{ $t('证件照') }}/护照上传</p>
            <div style="display: flex; justify-content: space-between">
              <div style="text-align: center">
                <el-upload :auto-upload="false" :limit="1" action="#" list-type="picture-card">
                  <i slot="default" class="el-icon-plus"></i>
                  <div slot="file" slot-scope="{ file }">
                    <img :src="file.url" alt="" class="el-upload-list__item-thumbnail"/>
                    <span class="el-upload-list__item-actions">
                                                                                    <span
                                                                                        class="el-upload-list__item-preview"
                                                                                        @click="handlePictureCardPreview(file)">
                                                                                      <i class="el-icon-zoom-in"></i>
                                                                                    </span>
                                                                                    <span v-if="!disabled"
                                                                                          class="el-upload-list__item-delete"
                                                                                          @click="handleRemove(file)">
                                                                                      <i class="el-icon-delete"></i>
                                                                                    </span>
                                                                                  </span>
                  </div>
                </el-upload>
                <p>{{ $t('证件照正面') }}</p>
              </div>
              <div style="text-align: center">
                <el-upload :auto-upload="false" :limit="1" action="#" list-type="picture-card">
                  <i slot="default" class="el-icon-plus"></i>
                  <div slot="file" slot-scope="{ file }">
                    <img :src="file.url" alt="" class="el-upload-list__item-thumbnail"/>
                    <span class="el-upload-list__item-actions">
                                                                                    <span
                                                                                        class="el-upload-list__item-preview"
                                                                                        @click="handlePictureCardPreview(file)">
                                                                                      <i class="el-icon-zoom-in"></i>
                                                                                    </span>
                                                                                    <span v-if="!disabled"
                                                                                          class="el-upload-list__item-delete"
                                                                                          @click="handleRemove(file)">
                                                                                      <i class="el-icon-delete"></i>
                                                                                    </span>
                                                                                  </span>
                  </div>
                </el-upload>
                <p>{{ $t('证件照反面') }}</p>
              </div>
              <div style="text-align: center">
                <el-upload :auto-upload="false" :limit="1" action="#" list-type="picture-card">
                  <i slot="default" class="el-icon-plus"></i>
                  <div slot="file" slot-scope="{ file }">
                    <img :src="file.url" alt="" class="el-upload-list__item-thumbnail"/>
                    <span class="el-upload-list__item-actions">
                                                                                    <span
                                                                                        class="el-upload-list__item-preview"
                                                                                        @click="handlePictureCardPreview(file)">
                                                                                      <i class="el-icon-zoom-in"></i>
                                                                                    </span>
                                                                                    <span v-if="!disabled"
                                                                                          class="el-upload-list__item-delete"
                                                                                          @click="handleRemove(file)">
                                                                                      <i class="el-icon-delete"></i>
                                                                                    </span>
                                                                                  </span>
                  </div>
                </el-upload>
                <p>{{ $t('手持证件照') }}</p>
              </div>
            </div>
            <img alt="" src="@/assets/images/users/u608.png" style="width: 100%"/>
          </el-form-item>
          <el-form-item>
            <p>{{ $t('邮箱') }}</p>
            <div class="m-btn">
              <span :class="{ active: active }" @click="active = true">{{ $t('邮箱') }}</span>
              <span :class="{ active: !active }" @click="active = false">{{ $t('手机号') }}</span>
            </div>
          </el-form-item>
          <el-form-item v-if="active">
            <p>{{ $t('邮箱') }}</p>
            <el-input :placeholder="$t('请填写电子邮箱')"></el-input>
          </el-form-item>
          <el-form-item v-else>
            <p>{{ $t('手机号') }}</p>
            <div style="display: flex">
              <el-select v-model="startValue" :placeholder="$t('请选择')" style="width: 120px; margin-right: 20px">

                <el-option v-for="item in startOptions" :key="item.value" :label="item.label" :value="item.value">
                </el-option>

              </el-select>
              <el-input :placeholder="$t('请输入手机号')"></el-input>
            </div>
          </el-form-item>
          <el-form-item>
            <p>{{ $t('邮箱') }}</p>
            <div style="display: flex">
              <el-input :placeholder="$t('请输入验证码')" style="margin-right: 10px"></el-input>
              <el-button v-if="!getCode" style="width: 140px" type="primary" @click="getCodes">{{ $t('邮箱') }}
              </el-button>
              <p v-else style="width: 120px; text-align: center">
                {{ codeCount }}
              </p>
            </div>
          </el-form-item>
          <el-form-item>
            <p>{{ $t('输入登录密码') }}</p>
            <el-input :placeholder="$t('请输入登录密码')" show-password></el-input>
          </el-form-item>
          <el-form-item>
            <p>{{ $t('再次输入确认登录密码') }}</p>
            <el-input :placeholder="$t('请再输入登录密码')" show-password></el-input>
          </el-form-item>
          <el-form-item>
            <p>{{ $t('邀请码') }}（必填）</p>
            <el-input :placeholder="$t('请填写邀请码')"></el-input>
          </el-form-item>
        </el-form>
        <el-button style="width: 100%" type="primary">{{ $t('提交申请') }}</el-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "merchandise",
  data() {
    return {
      active: true
    };
  },
};
</script>

<style lang="scss" scoped>
.merchandise {
  background-color: #f0f2f5;
  padding: 20px;
  // height: 100%;
  .main {
    padding: 20px;
    background-color: #fff;
    margin-bottom: 10px;
    border-radius: 10px;
    border: 1px solid rgba(215, 215, 215, 1);

    .main-c {
      width: 30%;

      .m-btn {
        .active {
          background-color: rgba(51, 51, 51, 1);
          color: #fff;
        }

        span {
          display: inline-block;
          padding: 3px 0;
          height: 40px;
          width: 80px;
          border-radius: 5px;
          text-align: center;
          color: #666666;
          margin-right: 10px;
        }
      }
    }
  }
}
</style>
