#project: p3
#submitter: kmconrad3
#partner: none
#hours: 17

import os, zipfile, selenium, time
import pandas as pd
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

class GraphScraper:
    
    def __init__(self):
        self.visited = set()
        self.BFSorder = []
        self.DFSorder = []
        
    def go(self, node):
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        self.visited.add(node)
        chil = self.go(node)
        for ch in chil:
            if ch not in self.visited:
                self.visited.add(ch)
                self.dfs_search(ch)
    
    def bfs_search(self, node):
        todo = [node]
        count = set()
        count.add(node)
        while len(todo) > 0:
            curr = todo.pop(0)
            chil = self.go(curr)
            for ch in chil:
                if ch not in count:
                    todo.append(ch)
                    count.add(ch)



class FileScraper(GraphScraper):
        
    def go(self, node):
        with open("file_nodes/" + node + ".txt", "r") as f:
            lines = f.readlines()
            self.BFSorder.append(lines[2][5])
            self.DFSorder.append(lines[3][5])
            children = lines[1].split()
        return children



class WebScraper(GraphScraper):
    
    def	__init__(self, driver=None):
        super().__init__()
        self.driver = driver

    def go(self, url): #visit the node, add each password number to the proper list
        mylinks = []
        self.driver.get(url)
        try:
            dfs_el = self.driver.find_element_by_id("DFS")
            dfs_el.click()
            self.DFSorder.append(dfs_el.text)
        except NoSuchElementException:
            pass
        try:
            bfs_el = self.driver.find_element_by_id("BFS")
            bfs_el.click()
            self.BFSorder.append(bfs_el.text)
        except NoSuchElementException:
            pass
        link = self.driver.find_elements_by_tag_name("a")
        for li in link:
            mylinks.append(li.get_attribute("href"))
        return mylinks
        
    def dfs_pass(self, start_url):
        self.DFSorder = []
        self.visited = set()
        self.dfs_search(start_url)
        return ("".join(self.DFSorder))

    def bfs_pass(self, start_url):
        self.BFSorder = []
        self.bfs_search(start_url)
        return ("".join(self.BFSorder))

    def protected_df(self, url, password):
        self.driver.get(url)
        for i in list(password):
            btnid = "btn" + i
            try:
                btn = self.driver.find_element_by_id(btnid)
                btn.click()
            except NoSuchElementException:
                pass
        try:
            btn = self.driver.find_element_by_id("attempt-button")
            btn.click()
        except NoSuchElementException:
            pass
        time.sleep(3)
        page_source = self.driver.page_source
        try:
            btn = self.driver.find_element_by_id("more-locations-button")
            btn.click()
        except NoSuchElementException:
            pass
        time.sleep(1)
        newsour = self.driver.page_source
        while page_source != newsour:
            hold = newsour
            try:
                btn = self.driver.find_element_by_id("more-locations-button")
                btn.click()
            except NoSuchElementException:
                pass
            time.sleep(1)
            newsour = self.driver.page_source
            page_source = hold
        return pd.read_html(newsour)[0]
                
                                              