package com.example.demo.Entities;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
public class Status {
    @Id
    private int id;
    private String status;

    public Status(int id, String status) {
        this.id = id;
        status = status;
    }


    public Status() {

    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
    @Override
    public String toString() {
        return this.status + this.id;
    }

}

