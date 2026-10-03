<template>
  <div style="display:flex; gap:10px;">
    <div ref="container" style="width:70%;height:600px;border:1px solid #eee;"></div>
    <!-- 详情面板 -->
    <div v-if="showPanel" style="width:28%;border:1px solid #ccc;padding:16px;border-radius:6px;">
      <h3>{{ currentNode.label }}</h3>
      <p>节点ID：{{ currentNode.id }}</p>
      <p>这是节点详情描述，可以后续对接后端拿到更多信息</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import G6 from '@antv/g6';

const container = ref(null);
const showPanel = ref(false);
const currentNode = ref({});

onMounted(() => {
  const graph = new G6.Graph({
    container: container.value,
    width: 800,
    height: 600,
    layout: {
      type: 'force',
      linkDistance: 120,
      nodeStrength: -300
    },
    defaultNode: {
      type: 'rect',
      size: [100, 40],
      style: {
        fill: '#fff',
        stroke: '#4096ff',
        lineWidth: 2
      },
      labelCfg: {
        style: {
          fill: '#333'
        }
      },
      stateStyles: {
        hover: {
          fill: '#e6f4ff',
          stroke: '#1677ff',
          lineWidth:3
        }
      }
    },
    defaultEdge: {
      type: 'line',
      style: {
        stroke: '#999',
        lineWidth:2,
        endArrow: true
      }
    },
    modes: {
      default: ['drag-canvas', 'drag-node', 'zoom-canvas']
    }
  });

  const data = {
    nodes: [
      { id: 'node1', label: '节点A' },
      { id: 'node2', label: '节点B' },
      { id: 'node3', label: '节点C' },
      { id: 'node4', label: '节点D' },
      { id: 'node5', label: '节点E' },
    ],
    edges: [
      { source: 'node1', target: 'node2' },
      { source: 'node1', target: 'node3' },
      { source: 'node2', target: 'node4' },
      { source: 'node3', target: 'node5' },
    ]
  };

  graph.data(data);
  graph.render();

  // hover悬浮
  graph.on('node:mouseenter', (e) => {
    graph.setItemState(e.item, 'hover', true);
  });
  graph.on('node:mouseleave', (e) => {
    graph.setItemState(e.item, 'hover', false);
  });

  // 点击节点弹出详情面板
  graph.on('node:click', (e) => {
    currentNode.value = e.item.getModel();
    showPanel.value = true;
  });
  // 点击空白处关闭面板
  graph.on('canvas:click', () => {
    showPanel.value = false;
  });
})
</script>

<style scoped>
</style>
