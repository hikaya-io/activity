jquery.orgChart
===============

jquery plugin for org chart, use a javascript array as input.
inspired by https://github.com/caprica/jquery-orgchart

[see a demo here](http://www.mit.edu/~wangyu/jquery.orgChart/example.html)

Usage
-----

1. set up a <div/> as the container of org chart:

```html
<div id="orgChart"></div>
```

2. prepare your data in this format:

```javascript
var testData = [
    {id: 1, name: 'Acme Organization', parent: 0},
    {id: 2, name: 'CEO Office', parent: 1},
    {id: 3, name: 'Division 1', parent: 1},
    {id: 4, name: 'Division 2', parent: 1},
    {id: 6, name: 'Division 3', parent: 1},
    {id: 7, name: 'Division 4', parent: 1},
    {id: 8, name: 'Division 5', parent: 1},
    {id: 5, name: 'Sub Division', parent: 3},        
];
```

Every node is an object with (in minimum) id, name, and parent.

3. build orgnizational chart with:

```javascript
var orgChart = $('#orgChart').orgChart({data: testData});
```

the object return by the jQuery function could be used to invoke methods.


Option List
-----------

All the options are optional.

data: (Array) the initial data of the org chart.

showControls: (Boolean/false) on/off for display add or remove node button.

allowEdit: (Boolean/false) on/off for allowing users to click on the node's title to edit its name.

onAddNode(node): (Function) callback function when "Add Child" button is clicked. Note that this will prevent the node from automatically created, so developers need to call newNode(parentId) to actually create the node.

onDeleteNode(node): (Function) callback function when "Delete Node" button is clicked. Note that this will prevent the node from automatically deleted, so developers need to call deleteNode(id) to actually delete the node.

onClickNode(node): (Function) callback when a node is clicked. 

newNodeText: (String/"Add Child") text displayed on the "Add Child" button.

Note that in the callback options "onAddNode", "onDeleteNode", "onClickNode", a Node object will be passed as the parameter. You can access the data via node.data.


Methods
-------

startEdit(id): let a node enter edit mode.

newNode(parentId): create a node as a subnode of node number parentId.

addNode(data): add a node carrying specific data.

deleteNode(id): delete the node with specific id.

getData(): get all the node data of the org chart in an array.


License
-------
MIT