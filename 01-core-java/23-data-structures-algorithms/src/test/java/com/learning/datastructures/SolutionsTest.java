package com.learning.datastructures;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import com.learning.datastructures.DataStructuresSolutions.LRUCache;
import com.learning.datastructures.DataStructuresSolutions.Trie;
import com.learning.datastructures.TreeSolutions.TreeNode;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Focused unit tests for the pure-algorithm solution classes.
 * These classes are not exercised by the demo entry points, so direct
 * tests provide both behavioral verification and coverage.
 */
@DisplayName("Solutions Tests")
class SolutionsTest {

    @Nested
    @DisplayName("Sorting Solutions")
    class SortingTests {

        @Test
        @DisplayName("mergeSort sorts an unsorted array")
        void mergeSortSorts() {
            int[] arr = {5, 2, 9, 1, 5, 6};
            SortingSolutions.mergeSort(arr, 0, arr.length - 1);
            assertThat(arr).containsExactly(1, 2, 5, 5, 6, 9);
        }

        @Test
        @DisplayName("mergeSort handles single element and empty ranges")
        void mergeSortEdgeCases() {
            int[] single = {42};
            SortingSolutions.mergeSort(single, 0, 0);
            assertThat(single).containsExactly(42);
        }

        @Test
        @DisplayName("quickSort sorts an unsorted array")
        void quickSortSorts() {
            int[] arr = {10, 7, 8, 9, 1, 5};
            SortingSolutions.quickSort(arr, 0, arr.length - 1);
            assertThat(arr).containsExactly(1, 5, 7, 8, 9, 10);
        }

        @Test
        @DisplayName("quickSort handles already sorted input")
        void quickSortSorted() {
            int[] arr = {1, 2, 3};
            SortingSolutions.quickSort(arr, 0, arr.length - 1);
            assertThat(arr).containsExactly(1, 2, 3);
        }

        @Test
        @DisplayName("binarySearch finds present and absent targets")
        void binarySearchFinds() {
            int[] arr = {1, 3, 5, 7, 9};
            assertThat(SortingSolutions.binarySearch(arr, 5)).isEqualTo(2);
            assertThat(SortingSolutions.binarySearch(arr, 1)).isEqualTo(0);
            assertThat(SortingSolutions.binarySearch(arr, 9)).isEqualTo(4);
            assertThat(SortingSolutions.binarySearch(arr, 4)).isEqualTo(-1);
            assertThat(SortingSolutions.binarySearch(new int[0], 1)).isEqualTo(-1);
        }
    }

    @Nested
    @DisplayName("Graph Solutions")
    class GraphTests {

        private List<List<Integer>> adjacency() {
            List<List<Integer>> adj = new ArrayList<>();
            for (int i = 0; i < 4; i++) {
                adj.add(new ArrayList<>());
            }
            adj.get(0).add(1);
            adj.get(0).add(2);
            adj.get(1).add(2);
            adj.get(2).add(3);
            return adj;
        }

        @Test
        @DisplayName("bfs visits nodes in breadth-first order")
        void bfsOrder() {
            assertThat(GraphSolutions.bfs(4, adjacency(), 0)).containsExactly(0, 1, 2, 3);
        }

        @Test
        @DisplayName("dfs visits every reachable node")
        void dfsVisitsAll() {
            assertThat(GraphSolutions.dfs(4, adjacency(), 0)).containsExactly(0, 1, 2, 3);
        }

        @Test
        @DisplayName("dijkstra computes shortest paths and leaves unreachable at max value")
        void dijkstraShortestPaths() {
            List<List<int[]>> adj = new ArrayList<>();
            for (int i = 0; i < 4; i++) {
                adj.add(new ArrayList<>());
            }
            adj.get(0).add(new int[]{1, 10});
            adj.get(0).add(new int[]{2, 1});
            adj.get(2).add(new int[]{1, 1});
            adj.get(1).add(new int[]{3, 4});
            int[] dist = GraphSolutions.dijkstra(4, adj, 0);
            assertThat(dist).containsExactly(0, 2, 1, 6);
        }

        @Test
        @DisplayName("dijkstra ignores stale queue entries")
        void dijkstraStaleEntries() {
            List<List<int[]>> adj = new ArrayList<>();
            for (int i = 0; i < 3; i++) {
                adj.add(new ArrayList<>());
            }
            adj.get(0).add(new int[]{1, 100});
            adj.get(0).add(new int[]{2, 1});
            adj.get(2).add(new int[]{1, 1});
            int[] dist = GraphSolutions.dijkstra(3, adj, 0);
            assertThat(dist).containsExactly(0, 2, 1);
        }
    }

    @Nested
    @DisplayName("Tree Solutions")
    class TreeTests {

        private TreeNode bst() {
            TreeNode root = new TreeNode(4);
            root.left = new TreeNode(2);
            root.right = new TreeNode(6);
            root.left.left = new TreeNode(1);
            root.left.right = new TreeNode(3);
            root.right.left = new TreeNode(5);
            root.right.right = new TreeNode(7);
            return root;
        }

        @Test
        @DisplayName("inorder traversal yields sorted values")
        void inorderYieldsSorted() {
            List<Integer> result = new ArrayList<>();
            TreeSolutions.inorderTraversal(bst(), result);
            assertThat(result).containsExactly(1, 2, 3, 4, 5, 6, 7);
        }

        @Test
        @DisplayName("inorder traversal handles null root")
        void inorderNullRoot() {
            List<Integer> result = new ArrayList<>();
            TreeSolutions.inorderTraversal(null, result);
            assertThat(result).isEmpty();
        }

        @Test
        @DisplayName("preorder traversal yields root-first order")
        void preorderYieldsRootFirst() {
            List<Integer> result = new ArrayList<>();
            TreeSolutions.preorderTraversal(bst(), result);
            assertThat(result).containsExactly(4, 2, 1, 3, 6, 5, 7);
        }

        @Test
        @DisplayName("preorder traversal handles null root")
        void preorderNullRoot() {
            List<Integer> result = new ArrayList<>();
            TreeSolutions.preorderTraversal(null, result);
            assertThat(result).isEmpty();
        }

        @Test
        @DisplayName("level order groups values by depth")
        void levelOrderGroups() {
            assertThat(TreeSolutions.levelOrder(bst()))
                    .containsExactly(List.of(4), List.of(2, 6), List.of(1, 3, 5, 7));
            assertThat(TreeSolutions.levelOrder(null)).isEmpty();
        }

        @Test
        @DisplayName("isValidBST accepts valid and rejects invalid trees")
        void validatesBst() {
            assertThat(TreeSolutions.isValidBST(bst())).isTrue();
            assertThat(TreeSolutions.isValidBST(null)).isTrue();
            TreeNode bad = new TreeNode(5);
            bad.left = new TreeNode(1);
            bad.right = new TreeNode(4);
            bad.right.left = new TreeNode(3);
            bad.right.right = new TreeNode(6);
            assertThat(TreeSolutions.isValidBST(bad)).isFalse();
        }

        @Test
        @DisplayName("lowestCommonAncestor finds split and ancestor cases")
        void findsLca() {
            TreeNode root = bst();
            assertThat(TreeSolutions.lowestCommonAncestor(root, root.left.left, root.left.right))
                    .isSameAs(root.left);
            assertThat(TreeSolutions.lowestCommonAncestor(root, root.left, root.right))
                    .isSameAs(root);
            assertThat(TreeSolutions.lowestCommonAncestor(root, root.left, root.left.right))
                    .isSameAs(root.left);
            assertThat(TreeSolutions.lowestCommonAncestor(null, null, null)).isNull();
        }
    }

    @Nested
    @DisplayName("Dynamic Programming Solutions")
    class DynamicProgrammingTests {

        @Test
        @DisplayName("coinChange returns minimum coins or -1 when impossible")
        void coinChangeMinCoins() {
            assertThat(DynamicProgrammingSolutions.coinChange(new int[]{1, 2, 5}, 11)).isEqualTo(3);
            assertThat(DynamicProgrammingSolutions.coinChange(new int[]{2}, 3)).isEqualTo(-1);
            assertThat(DynamicProgrammingSolutions.coinChange(new int[]{1}, 0)).isEqualTo(0);
        }

        @Test
        @DisplayName("lengthOfLIS handles typical, empty and null input")
        void lengthOfLis() {
            assertThat(DynamicProgrammingSolutions.lengthOfLIS(
                    new int[]{10, 9, 2, 5, 3, 7, 101, 18})).isEqualTo(4);
            assertThat(DynamicProgrammingSolutions.lengthOfLIS(new int[0])).isEqualTo(0);
            assertThat(DynamicProgrammingSolutions.lengthOfLIS(null)).isEqualTo(0);
        }

        @Test
        @DisplayName("knapsack picks the optimal item set")
        void knapsackOptimal() {
            assertThat(DynamicProgrammingSolutions.knapsack(
                    50, new int[]{10, 20, 30}, new int[]{60, 100, 120})).isEqualTo(220);
            assertThat(DynamicProgrammingSolutions.knapsack(
                    5, new int[]{10}, new int[]{60})).isEqualTo(0);
        }

        @Test
        @DisplayName("maxSubArray handles mixed and all-negative input")
        void maxSubArray() {
            assertThat(DynamicProgrammingSolutions.maxSubArray(
                    new int[]{-2, 1, -3, 4, -1, 2, 1, -5, 4})).isEqualTo(6);
            assertThat(DynamicProgrammingSolutions.maxSubArray(new int[]{-3, -1, -2})).isEqualTo(-1);
        }
    }

    @Nested
    @DisplayName("Data Structure Solutions")
    class DataStructureTests {

        @Test
        @DisplayName("LRU cache evicts least recently used entries")
        void lruCacheEvicts() {
            LRUCache cache = new LRUCache(2);
            assertThat(cache.get(1)).isEqualTo(-1);
            cache.put(1, 1);
            cache.put(2, 2);
            assertThat(cache.get(1)).isEqualTo(1);
            cache.put(3, 3);
            assertThat(cache.get(2)).isEqualTo(-1);
            cache.put(1, 10);
            assertThat(cache.get(1)).isEqualTo(10);
            cache.put(4, 4);
            assertThat(cache.get(3)).isEqualTo(-1);
            assertThat(cache.get(4)).isEqualTo(4);
        }

        @Test
        @DisplayName("Trie supports insert, search and prefix checks")
        void trieOperations() {
            Trie trie = new Trie();
            trie.insert("apple");
            assertThat(trie.search("apple")).isTrue();
            assertThat(trie.search("app")).isFalse();
            assertThat(trie.search("apricot")).isFalse();
            assertThat(trie.startsWith("app")).isTrue();
            assertThat(trie.startsWith("apl")).isFalse();
            trie.insert("app");
            assertThat(trie.search("app")).isTrue();
        }

        @Test
        @DisplayName("topologicalSort orders a DAG and rejects cycles")
        void topologicalSortOrders() {
            List<Integer> order = DataStructuresSolutions.topologicalSort(
                    4, new int[][]{{0, 1}, {0, 2}, {1, 3}, {2, 3}});
            assertThat(order).hasSize(4);
            assertThat(order.indexOf(0)).isLessThan(order.indexOf(1));
            assertThat(order.indexOf(0)).isLessThan(order.indexOf(2));
            assertThat(order.indexOf(1)).isLessThan(order.indexOf(3));
            assertThat(order.indexOf(2)).isLessThan(order.indexOf(3));
            assertThat(DataStructuresSolutions.topologicalSort(
                    2, new int[][]{{0, 1}, {1, 0}})).isEmpty();
        }
    }
}
