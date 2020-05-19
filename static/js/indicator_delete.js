
var itemId;
var activeButton;
/**
 * Set the Item to delete
 **/
function setIndicatorItemToDelete(id) {
	itemId = id;
}

/**
 * Redirect to the page to delete the item
 **/
function indicatorDeleteItem() {
	toastr.success('You have successfully delete the indicator');
	setTimeout(() => {
		window.location.href = `/indicators/indicator_delete/${itemId}/`;
	}, 2000);
}

/**
 * reload the page to close the modal
 **/
function indicatorDeleteCancel() {
	window.location.reload();
}
$(document).ready(() => {});