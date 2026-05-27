<template>
  <div class="app-container">
    <div style="margin:0 0 5px 20px">{{ $t('Fixed') }} header, sorted by header order,</div>
    <fixed-thead/>

    <div style="margin:30px 0 5px 20px">{{ $t('Not') }} fixed header, sorted by click{{ $t('order') }}</div>
    <unfixed-thead/>
  </div>
</template>

<script>
import FixedThead from './components/FixedThead'
import UnfixedThead from './components/UnfixedThead'

export default {
  name: 'DynamicTable',
  components: {FixedThead, UnfixedThead}
}
</script>
