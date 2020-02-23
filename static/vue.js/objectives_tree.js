// Tree component
Vue.component('tree-chart', {
    template: '#vue-tree-template',
    delimiters: ['[[', ']]'],
    props: ["json"],
    data() {
        return {
            treeData: {}
        }
    },
    watch: {
        json: {
            handler: function (Props) {
                let extendKey = function (jsonData) {
                    jsonData.extend = (jsonData.extend === void 0 ? true : !!jsonData.extend);
                    if (Array.isArray(jsonData.children)) {
                        jsonData.children.forEach(c => {
                            extendKey(c)
                        })
                    }
                    return jsonData;
                }
                if (Props) {
                    this.treeData = extendKey(Props);
                }
            },
            immediate: true
        }
    },
    methods: {
        toggleExtend: function (treeData) {
            treeData.extend = !treeData.extend;
            this.$forceUpdate();
        }
    }
});

// Start vue app
new Vue({
    delimiters: ['[[', ']]'],
    el: '#objectives_tree',
    data: {
        origData: JSON.parse(document.getElementById('objectives-data').textContent),
        treeData: {}
    },
    methods: {
        setProgram(name) {
            this.currentProgram = name;
            this.refreshTreeData();
        },
        refreshTreeData() {
            this.treeData = this.getChildren('0');
        },
        getChildren(nodeId) {
            const node = this.origData[nodeId];
            if (node.children.length === 0) {
                return {name: node.name}
            }
            const children = [];
            for (let i = 0; i < node.children.length; i++) {
                const childId = String(node.children[i]);
                if (this.origData[childId].program !== this.currentProgram) {
                    continue
                }
                children.push(this.getChildren(childId));
            }
            return {name: node.name, children: children}
        }
    }
});
