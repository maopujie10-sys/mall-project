<template>
  <div class="merchant-settled-content">
    <div class="merchant-settled-content-text">
      <p>Chapter I Overview</p>

      <p>
        Scope of application: This agreement applies to Shopee platform
        merchants, merchants can choose business model according to business
        needs to sell goods or provide services to buyers through the Shopee
        platform.
      </p>

      <p>
        1.1) Shopee for the majority of buyers to provide the best quality goods
        and services. To protect the legitimate rights and interests of Shopee
        merchants, to maintain the normal order of Shopee business, according to
        the "Shopee Terms of Service" and other services / cooperation
        agreements, the development of this agreement.
      </p>

      <p>
        1.2) Shopee platform general rules is to add basic obligations or
        regulate the exercise of basic rights of merchants resident in Shopee
        terms.
      </p>
      <p>
        1.3) rules behavior determination and processing, based on Shopee from a
        reasonable perspective combined with the evidence provided by both
        parties to determine the facts, based on the relevant platform rules
        strictly enforced. shopee merchants are equal in the application of the
        rules.ants are equal in the applicationants are sd
      </p>

      <p>Chapter I Overview</p>

      <p>
        Scope of application: This agreement applies to Shopee platform
        merchants, merchants can choose business model according to business
        needs to sell goods or provide services to buyers through the Shopee
        platform.
      </p>
      <p>
        1.1) Shopee for the majority of buyers to provide the best quality goods
        and services. To protect the legitimate rights and interests of Shopee
        merchants, to maintain the normal order of Shopee business, according to
        the "Shopee Terms of Service" and other services / cooperation
        agreements, the development of this agreement.
      </p>
      <p>
        1.2) Shopee platform general rules is to add basic obligations or
        regulate the exercise of basic rights of merchants resident in Shopee
        terms.
      </p>
      <p>
        1.3) rules behavior determination and processing, based on Shopee from a
        reasonable perspective combined with the evidence provided by both
        parties to determine the facts, based on the relevant platform rules
        strictly enforced. shopee merchants are equal in the application of the
        rules.
      </p>
      <p>
        1.4) merchants should comply with national laws, administrative
        regulations, departmental regulations and other regulatory documents.
        Any suspected violations of national laws, administrative regulations,
        departmental regulations and other regulatory documents, the Agreement
        has been provided for, the Agreement applies; the Agreement has not been
        provided for, Shopee has the right to deal with the corresponding rules
        at its discretion, but Shopee does not exempt merchants from legal
        liability for violations of law, breach of contract and other acts.
      </p>
      <p>
        1.5) Any behavior of the merchant in Shopee, shall also comply with the
        agreements entered into with Shopee.
      </p>
      <p>
        1.6)Shopee has the right to change this agreement at any time and
        announced on the platform home page or merchant management system and
        other channels. If the merchant does not agree with the changes, should
        immediately stop using the relevant services provided by the Shopee
        platform, and promptly notify Shopee. Shopee has the right to
        unilaterally determine the behavior of the merchant and the
        rules/agreements that should apply, and deal with them accordingly.
      </p>
    </div>
    <div class="merchant-settled-content-agreement">
      <el-checkbox v-model="checked">
        <span class="text">I have read and agree to the</span>
        <span class="agreement-link">《Occupancy Agreement》</span>
      </el-checkbox>
      <div class="agreement-btn">
        <el-button type="primary">Agree</el-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EsAgreeText',
  data() {
    return {
      checked: false,
    }
  },
}
</script>

<style lang="scss">
.merchant-settled-content {
  position: relative;
  background-color: var(--color-white);
  padding: 0 20px;
  &-text {
    border-radius: 4px;
    border: 1px solid var(--color-border);
    position: relative;
    top: -90px;
    background-color: var(--color-white);
    padding: 24px;
    p {
      margin-bottom: 10px;
      line-height: 1.5em;
    }
  }

  &-agreement {
    font-weight: 500;
    font-size: 12px;
    width: 100%;
    text-align: center;
    margin: -60px 0 100px 0;
    .text {
      color: var(--color-black);
    }
    .agreement-link {
      font-weight: 400;
      color: var(--color-main);
      margin-left: 4px;
    }
    .agreement-btn {
      margin-top: 50px;
      .el-button {
        width: 100%;
        max-width: 475px;
        height: 52px;
        font-weight: 400;
        font-size: 16px;
      }
    }
  }
}
</style>
