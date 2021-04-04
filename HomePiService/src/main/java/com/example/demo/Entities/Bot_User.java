package com.example.demo.Entities;

import javax.persistence.*;

@Entity
@Table(name="bot_user",schema = "public")
public class Bot_User {
    @Id
    private Integer id;
    private String firstname;
    private String lastname;
    private String username;
    private String languagecode;
    private boolean isbot;
    @ManyToOne(cascade = CascadeType.REFRESH,fetch=FetchType.EAGER, targetEntity=Status.class)
    @JoinColumn(name = "status", nullable = false)
    private Status status;

    public Bot_User(Integer id, String firstname, String lastname, String username, String languagecode, boolean isbot, Status status) {
        this.id = id;
        this.firstname = firstname;
        this.lastname = lastname;
        this.username = username;
        this.languagecode = languagecode;
        this.isbot = isbot;
        this.status = status;
    }

    public Bot_User() {

    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getFirstname() {
        return firstname;
    }

    public void setFirstname(String firstName) {
        this.firstname = firstName;
    }

    public String getLastname() {
        return lastname;
    }

    public void setLastname(String lastName) {
        this.lastname = lastName;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String userName) {
        this.username = userName;
    }

    public String getLanguagecode() {
        return languagecode;
    }

    public void setLanguagecode(String languageCode) {
        this.languagecode = languageCode;
    }

    public Status getStatus() {
        return status;
    }

    public void setStatus(Status status) {
        this.status = status;
    }

    public boolean getisIsbot() {
        return isbot;
    }

    public void setIsbot(boolean isbot) {
        this.isbot = isbot;
    }

    @Override
    public String toString() {
        return this.status.toString();
    }
}

